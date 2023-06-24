import os
import sys
import cv2
import numpy as np
import shutil
from typing import List


def cut_video(video_path: str) -> None:
    try:
        os.mkdir("dataset_photos")
    except FileExistsError:
        os.rmdir("dataset_photos")
        raise Exception(
            "Папка dataset_photos уже существует в данной директории!")
    counter = 1
    frame_counter = 1
    video = cv2.VideoCapture(video_path)
    ret, frame = video.read()
    while counter < 600:
        if (counter % 6 == 0):
            isWritten = cv2.imwrite(
                f"dataset_photos/{frame_counter}.jpg", frame)
            frame_counter += 1
        ret, frame = video.read()
        counter += 1


def nothing(x):
    """"""
    pass


def try_color_settings() -> None:
    """Функция подборки цветов, для более точного определения образов"""
    cap = cv2.VideoCapture("C:\\Users\\user\\Downloads\\dataset_video.mp4")
    cv2.namedWindow("frame1")

    cv2.createTrackbar("HL", "frame1", 0, 180, nothing)
    cv2.createTrackbar("SL", "frame1", 0, 255, nothing)
    cv2.createTrackbar("VL", "frame1", 0, 255, nothing)

    cv2.createTrackbar("H", "frame1", 0, 180, nothing)
    cv2.createTrackbar("S", "frame1", 0, 255, nothing)
    cv2.createTrackbar("V", "frame1", 0, 255, nothing)

    cv2.setTrackbarPos("HL", "frame1", 2)
    cv2.setTrackbarPos("SL", "frame1", 116)
    cv2.setTrackbarPos("VL", "frame1", 187)

    cv2.setTrackbarPos("H", "frame1", 102)
    cv2.setTrackbarPos("S", "frame1", 255)
    cv2.setTrackbarPos("V", "frame1", 255)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (700, 700))
        # frame = cv2.medianBlur(frame, 3)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        hl = cv2.getTrackbarPos("HL", "frame1")
        sl = cv2.getTrackbarPos("SL", "frame1")
        vl = cv2.getTrackbarPos("VL", "frame1")

        h = cv2.getTrackbarPos("H", "frame1")
        s = cv2.getTrackbarPos("S", "frame1")
        v = cv2.getTrackbarPos("V", "frame1")

        lower = np.array([hl, sl, vl])
        upper = np.array([h, s, v])
        mask = cv2.inRange(hsv, lower, upper)

        mask = cv2.dilate(mask, kernel, iterations=10)

        contours, hierarhy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour=contour) > 400:
                x, y, w, h = cv2.boundingRect(contour)
                frame = cv2.rectangle(
                    frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        res = cv2.bitwise_and(frame, frame, mask=mask)

        height, width = res.shape[:2]
        # res = cv2.resize(frame, (height * 2, width * 2),
        #                  interpolation=cv2.INTER_CUBIC)

        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("res", res)

        k = cv2.waitKey(1) & (0xFF)
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def get_photo_directory_folder() -> None:
    """Вспомогательная функция для формирования папки с датасетом, на основе проставленных якорей"""
    label_list = [file_name[:-4] for file_name in os.listdir("label_dir")]
    print(label_list)
    for label in label_list:
        shutil.move(f"image_dir/{label}.jpg", f"dataset_photos/{label}.jpg")


def get_train_and_test_data() -> None:
    """Формирование датасета для модели YOLOv8"""
    test_count = 30

    label_list = os.listdir("label_dir")
    image_list = os.listdir("dataset_photos")

    for i in range(test_count):
        shutil.copyfile(
            f"label_dir/{label_list[i]}", f"test/labels/{label_list[i]}")
        shutil.copyfile(
            f"dataset_photos/{image_list[i]}", f"test/images/{image_list[i]}")


def read_with_delay(cap) -> tuple[bool, List]:
    """Функция получения каждого N-го кадра видео"""
    delay_counter = 5
    ret, frame = cap.read()
    while delay_counter > 0 and ret:
        ret, frame = cap.read()
        delay_counter -= 1

    return (ret, frame)


def get_changes_mass(frame, before_frame):
    """Получение маски изменения всего на изображении"""
    mask = np.zeros(frame.shape)
    for y in range(frame.shape[0]):
        for x in range(frame.shape[1]):
            pixel_from_frame = int(frame[y, x])
            pixel_from_before_frame = int(before_frame[y, x])
            if (abs(pixel_from_before_frame - pixel_from_frame) > 60):
                mask[y, x] = 255
    return mask


def detect_move_objects() -> None:
    """Выявление движущихся (изменяющихся) элементов на фотографии"""
    cap = cv2.VideoCapture("C:\\Users\\user\\Downloads\\dataset_video.mp4")

    ret, before_frame = cap.read()
    ret, frame = read_with_delay(cap)
    while ret:

        frame = cv2.resize(frame, (700, 700), cv2.INTER_LINEAR)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_before_frame = cv2.cvtColor(before_frame, cv2.COLOR_BGR2GRAY)
        mask = get_changes_mass(gray_frame, gray_before_frame)

        kernel5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel)
        # mask = cv2.dilate(mask, kernel=kernel)
        mask = np.array(mask, dtype=np.uint8)
        # mask = cv2.erode(mask, kernel=kernel5)
        # mask = cv2.dilate(mask, kernel=kernel5, iterations=5)

        contours, hierarhy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        before_frame = frame
        for cont in contours:
            if cv2.contourArea(cont) > 200:
                x, y, w, h = cv2.boundingRect(cont)
                frame = cv2.rectangle(
                    frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)
        if cv2.waitKey(1) == ord('q'):
            break

        ret, frame = read_with_delay(cap)


if __name__ == "__main__":
    # video_path = "C:\\Users\\user\\Downloads\\dataset_video.mp4"
    # cut_video(video_path=video_path)
    # try_color_settings()
    # get_photo_directory_folder()
    # get_train_and_test_data()
    detect_move_objects()
