from typing import NamedTuple, Any
import cv2
import numpy as np
import json
import os
import time
from ultralytics import YOLO
from enum import Enum
from collections import namedtuple


class Coordinate(NamedTuple):
    x1: int
    y1: int
    x2: int
    y2: int


class Event(Enum):
    """Виды событий"""
    TRANSPORT_ON_CAMERA = 0,
    TRANSPOT_OFF_CAMERA = 1,
    TRANSPORT_WORKING = 2,
    TRANSPORT_CHILLING = 3,


class TransportType(Enum):
    """Виды событий"""
    TRUCK = 0,
    EXCAVATOR = 1,
    TRACTOR = 2,
    LIFTING_CRANE = 3,


class Event_Tuple(NamedTuple):
    event_id: int
    time: int
    time_end: int
    transport_name: str
    event: Event
    coords: Coordinate
