import numpy as np
from typing import List, Union
from shapely.geometry import Polygon
from shapely.affinity import rotate
class Calculator:
    """
    Implements base calculations used by multiple classess
    """

    def _get_azimuth(self, point1, point2) -> float:
        azimuth = np.degrees(np.arctan2((point2[0] - point1[0]), (point2[1] - point1[1])))
        degrees = (azimuth + 360) % 360
        return degrees

    def _rotate_wall(
        self,
        wall: Polygon,
        degrees: float,
        required_angle: int = 45
    ) -> Polygon:
        if degrees > required_angle:
            angle = (degrees - required_angle)
        else:
            angle = (required_angle - degrees) * -1
        rotated_poly = rotate(geom=wall, angle=angle, origin=wall.exterior.coords[0])
        return rotated_poly

    def _get_min_max_indices(self, polygon: Polygon) -> Union[List, List]:
        argmin = np.argmin(polygon.exterior.coords, axis=0).tolist()
        argmax = np.argmax(polygon.exterior.coords, axis=0).tolist()
        return argmin, argmax
