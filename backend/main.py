from datetime import datetime
import cv2
import numpy as np
import json
import uuid
from neural_network import NEURAL_PATH, get_classes_mass
from ultralytics import YOLO
from collections import namedtuple
from typing import NamedTuple
from math import sqrt

from events import Event, TransportType, Event_Tuple, Coordinate

NEURAL_PATH = "new2.pt"
MAX_DISTANCE = 15


class Transport_cache_item(NamedTuple):
    name: str
    coord: Coordinate


def check_distance(coord1: Coordinate, coord2: Coordinate) -> bool:
    if (abs(int(coord1.x1) - int(coord2.x1)) < MAX_DISTANCE and abs(int(coord1.y1) - int(coord2.y1)) < MAX_DISTANCE):
        return True
    return False

class Cache():
    def __init__(self) -> None:
        self.cahce_size = 15
        self.cache_stack = []
        self.cache_different_objects = []
        self.cache_transport_counter = {
            "truck": 0, "excavator": 0, "tractor": 0, "lifting_crane": 0}
        self.cache_pointer = 0

    def check_in_cache(self, coord, cls: str) -> bool:
        """Проверка находится ли распознанный объект в кэше

        Если нет - то он занесется в него с новым названием, в противном случае сохранится под старым названием
        """
        # Цикл проверки, есть ли в кэше объект (по координатам вершин)
        for cache_submass in self.cache_stack:
            for item_mass in cache_submass:
                if check_distance(coord, item_mass.coord):
                    transport_cache_item = Transport_cache_item(
                        item_mass.name, coord=coord)
                    self.cache_stack[self.cache_pointer].append(
                        transport_cache_item)
                    return True

        # Если нет, то обновление счетчика и добавления нового объекта в кэш
        self.cache_transport_counter[cls] = self.cache_transport_counter[cls] + 1
        transport_cache_item = Transport_cache_item(
            f"{cls} {self.cache_transport_counter[cls]}", coord=coord)
        self.cache_stack[self.cache_pointer].append(
            transport_cache_item)

        return False


def change_cache_pointer(cache: Cache):
    """Функция проверки указателя кэша, в случае переполнения откат"""
    cache.cache_pointer += 1
    if (cache.cache_pointer == cache.cahce_size):
        cache.cache_pointer = 0
    cache.cache_stack[cache.cache_pointer] = []


def start_neural_network(video_path: str):
    model = YOLO(NEURAL_PATH)
    cache = Cache()
    second_of_video = 0
    json_dict = {}

    for _ in range(cache.cahce_size):
        cache.cache_stack.append([])
    classes_mass = get_classes_mass()

    cap = cv2.VideoCapture(video_path)

    ret, frame = cap.read()
    video_size = frame.shape[:-1]

    vid_cod = cv2.VideoWriter_fourcc(*'H264')
    result_video = cv2.VideoWriter('result.mp4',
                                   vid_cod,
                                   6, (video_size[1], video_size[0]))
    while ret:
        change_cache_pointer(cache=cache)
        result = model.predict(frame)
        for detect_obj in result[0].boxes:
            # detect_obj.cls - содержит класс объекта
            # detect_obj.xyxy - содержит координаты
            x1, y1, x2, y2 = np.array(
                detect_obj.xyxy.numpy()[0], dtype=np.uint32)
            obj_coords = Coordinate(x1, y1, x2, y2)
            cache.check_in_cache(obj_coords,
                                 classes_mass[int(detect_obj.cls)])

        before_frame = frame

        # mask = neural_helper(frame, before_frame=before_frame)
        # mask = cv2.resize(mask, (700, 700))
        for obj in cache.cache_stack[cache.cache_pointer]:
            json_adder(json_dict, obj.name, obj.coord, second_of_video)
            x1, y1, x2, y2 = obj.coord
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, obj.name, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # frame = cv2.resize(frame, (700, 700))
        # # cv2.imshow("Mask", mask)
        # cv2.imshow("Frame", frame)
        # # time.sleep(3)
        # if cv2.waitKey(1) == ord("q"):
        #     break
        for _ in range(6):
            result_video.write(frame)
        ret, frame = read_with_delay(cap)
        second_of_video += 1
        if second_of_video == 60:
            change_last_item_in_dict(
                json_dict=json_dict, second=second_of_video)
            desiralize_json_dict(json_dict)
            result_video.release()
            break


def read_with_delay(cap) -> tuple:
    """Функция получения каждого N-го кадра видео"""
    delay_counter = 5
    ret, frame = cap.read()
    while delay_counter > 0 and ret:
        ret, frame = cap.read()
        delay_counter -= 1

    return (ret, frame)


def neural_helper(frame, before_frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    before_frame = cv2.cvtColor(before_frame, cv2.COLOR_BGR2GRAY)

    mask = np.zeros(gray_frame.shape, dtype=np.uint8)

    for y in range(gray_frame.shape[0]):
        for x in range(gray_frame.shape[1]):
            mask[y][x] = 255 if (
                abs(int(gray_frame[y][x])-int(before_frame[y][x]))) > 10 else 0
    return mask


def json_adder(json_dict: dict, name: str, coord: Coordinate, second_of_video: int):
    """Заполнение json-файла"""
    # Если элемента еще не было в логах, то добавляем его
    if json_dict.get(name) is None:
        new_event = [Event_Tuple(event_id=int(uuid.uuid4().time),
                                 time=second_of_video,
                                 time_end=0,
                                 transport_name=convert_transport_type(TransportType[name.split(" ")[
                                     0].upper()]),
                                 event=convert_event(
                                     Event.TRANSPORT_ON_CAMERA),
                                 coords=coord)]

        json_dict.setdefault(name, [new_event])
    else:
        event_from_log = json_dict.get(name)
        event_coords = event_from_log[0][-1].coords
        if check_distance(event_coords, coord):
            if event_from_log[-1][0].event == "Transport is working" or event_from_log[-1][0].event == "Transport on camera":
                new_event = [Event_Tuple(event_id=int(uuid.uuid4().time),
                                         time=second_of_video,
                                         time_end=0,
                                         transport_name=convert_transport_type(TransportType[name.split(" ")[
                                             0].upper()]),
                                         event=convert_event(
                                             Event.TRANSPORT_CHILLING),
                                         coords=coord)]

                tuple_for_change = event_from_log[-1][0]
                new_tuple = [Event_Tuple(event_id=tuple_for_change.event_id,
                                         time=tuple_for_change.time,
                                         time_end=second_of_video,
                                         transport_name=tuple_for_change.transport_name,
                                         event=tuple_for_change.event,
                                         coords=tuple_for_change.coords)]
                event_from_log.append(new_event)
                event_from_log[-2] = new_tuple
                json_dict.update({name: event_from_log})
        else:
            if event_from_log[-1][0].event == "Transport is chilling" or event_from_log[-1][0].event == "Transport on camera":
                new_event = [Event_Tuple(event_id=int(uuid.uuid4().time),
                                         time=second_of_video,
                                         time_end=0,
                                         transport_name=convert_transport_type(TransportType[name.split(" ")[
                                             0].upper()]),
                                         event=convert_event(
                                             Event.TRANSPORT_WORKING),
                                         coords=coord)]

                tuple_for_change = event_from_log[-1][0]
                new_tuple = [Event_Tuple(event_id=tuple_for_change.event_id,
                                         time=tuple_for_change.time,
                                         time_end=second_of_video,
                                         transport_name=tuple_for_change.transport_name,
                                         event=tuple_for_change.event,
                                         coords=tuple_for_change.coords)]
                event_from_log.append(new_event)
                event_from_log[-2] = new_tuple
                json_dict.update({name: event_from_log})


def desiralize_json_dict(json_dict: dict) -> None:
    print(dict)
    new_json_dict = {}
    for (key, value) in json_dict.items():
        value_mass = []
        for mass in value:
            value_mass.append({
                "event_id": mass[0].event_id,
                "time": convert_seconds(mass[0].time),
                "time_end": convert_seconds(mass[0].time_end),
                "transport_name": mass[0].transport_name,
                "event": mass[0].event,
                "coords": [int(coord) for coord in mass[0].coords]
            })
        new_json_dict[key] = value_mass

    with open('data.json', 'w') as f:
        json.dump(new_json_dict, f)

    data = ""
    with open('data.json', 'r') as file:
        data = file.read()

    json_file_data = json.loads(data)

    with open('data.json', 'w') as f:
        json.dump(json_file_data, f, indent=2)


def convert_event(event: Event) -> str:
    match event:
        case Event.TRANSPORT_ON_CAMERA:
            return "Transport on camera"
        case Event.TRANSPOT_OFF_CAMERA:
            return "Transport go away"
        case Event.TRANSPORT_WORKING:
            return "Transport is working"
        case Event.TRANSPORT_CHILLING:
            return "Transport is chilling"


def convert_transport_type(transport_type: TransportType) -> str:
    match transport_type:
        case TransportType.TRUCK:
            return "Truck"
        case TransportType.EXCAVATOR:
            return "Excavator"
        case TransportType.TRACTOR:
            return "Tractor"
        case TransportType.LIFTING_CRANE:
            return "Lifting Crane"


def convert_seconds(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    remaining_seconds = "0" + \
        str(remaining_seconds) if remaining_seconds < 10 else str(remaining_seconds)
    minutes = "0" + str(minutes) if minutes < 10 else str(minutes)
    hours = "0" + str(hours) if hours < 10 else str(hours)
    return f"{hours}:{minutes}:{remaining_seconds}"


def change_last_item_in_dict(json_dict: dict, second: int) -> dict:
    return_dict = {}
    for (key, value) in json_dict.items():
        value_tuple = value[-1][0]
        value[-1] = [Event_Tuple(event_id=value_tuple.event_id,
                                 time=value_tuple.time,
                                 time_end=second,
                                 transport_name=value_tuple.transport_name,
                                 event=value_tuple.event,
                                 coords=value_tuple.coords)]
        return_dict.setdefault(key, value)

    return return_dict


def main() -> None:
    start_neural_network("")


if __name__ == "__main__":
    main()