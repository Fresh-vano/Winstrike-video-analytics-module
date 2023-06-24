import numpy
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List
from time import sleep

NEURAL_PATH = "last.pt"
# PATH_TO_CLASSES = "classes.txt"
PATH_TO_CLASSES = "best_classes.txt"


def get_classes_mass() -> tuple[str, ...]:
    """Получение массива с классами, которые распознает модель"""
    with open(PATH_TO_CLASSES, "r") as file:
        classes_mass = file.read().split("\n")

    return classes_mass


# def start_neural_network(video_path: str) -> None:
#     """Старт работы нейнонной сети"""
#     model = YOLO(NEURAL_PATH)

#     classes_mass = get_classes_mass()
#     cap = cv2.VideoCapture(video_path)

#     ret, frame = cap.read()
#     while ret:
#         # gray = cv2.resize(frame, (700, 700))
#         # gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
#         # gray = cv2.medianBlur(gray, 3)

#         result = model.predict(frame)
#         for detect_obj in result[0].boxes:
#             cls = int(detect_obj.cls)
#             x1, y1, x2, y2 = np.array(
#                 detect_obj.xyxy.numpy()[0], dtype=np.uint32)
#             frame = cv2.rectangle(frame, (x1, y1),
#                                   (x2, y2), (200, 0, 50), 3)
#             cv2.putText(frame, classes_mass[cls], (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

#         resized_frame = cv2.resize(frame, (700, 700))
#         cv2.imshow("Frame", resized_frame)
#         # cv2.imshow("Gray", gray)
#         cv2.waitKey(1)
#         # if cv2.waitKey(1) and ord("q"):
#         #     break
#         ret, frame = cap.read()


# start_neural_network()
