from dataclasses import dataclass
from shapely.geometry import Point
import uuid


@dataclass
class BoundingBox:
    """
    Bounding box dataclass to store bbox information per surface id
    """
    surface_id: uuid
    lower_left: Point
    upper_left: Point
    upper_right: Point
    lower_right: Point
