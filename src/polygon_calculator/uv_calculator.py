from typing import Dict, List
import numpy as np
from cjio.models import Geometry
from shapely.affinity import rotate
from shapely.geometry import Polygon

from models.dataclass_mappings.surfaces import Surface_dataclass
from src.polygon_calculator.calculator import Calculator

class UVCalculator(Calculator):

    def __init__(self, building_id: str = 'example'):
        self.building_id = building_id

    def map_uv_appearance(
        self,
        appearance: Dict,
        surface: Surface_dataclass,
        textures_enabled: bool = False
    ) -> List:
        """
        This normalizes the surface coordinates (to 0-1) for each point
        and updates the appearance vertices-textures object.

        for walls we have the face on the lat + lon and z-axis starting from the top left
        (it doesn't matter which direction in lat/lon we go,we are only interested in the face)

        for roofs we have the face on lat and lon, we can drop the z axis for now
        since roofs are georeferenced, we start from the upper right corner of a roof viewed top-down.
        TODO: check for slanted roofs how the z-axis come into play.
        """
        texture_indices = []
        for shell in surface['surface']:
            first_point = shell[0]
            last_point = shell[-2]
            degrees = self._get_azimuth(first_point, last_point)
            rotated_poly = self._rotate_wall(
                wall=Polygon(shell),
                degrees=degrees,
                required_angle=45
            )
            argmin, argmax = self._get_min_max_indices(rotated_poly)
            lower_left_point = (shell[argmin[0]][0], shell[argmin[1]][1], shell[argmin[2]][2])
            upper_right_point = (shell[argmax[0]][0], shell[argmax[1]][1], shell[argmax[2]][2])

            # dummy array
            relative_points = np.empty([0, 3])

            if surface['type'] == 'WallSurface':
                relative_points = [np.subtract([point[0] + point[1], point[2]], [lower_left_point[0] + lower_left_point[1], lower_left_point[2]]) for point in shell]
            else:
                relative_points = [np.subtract([point[0], point[1]], [upper_right_point[0], upper_right_point[1]]) for point in shell]
            max_coords = np.max(relative_points, axis=-2)
            min_coords = np.min(relative_points, axis=-2)
            for point in relative_points:
                normalized_point = np.round(np.abs((point) / (max_coords - min_coords)), 2).tolist()
                texture_indices.append(len(appearance["vertices-texture"]))
                appearance["vertices-texture"].append(normalized_point)

        if textures_enabled:
            texture = {
                "type": "PNG",
                "image": f"/{self.building_id}/{surface['id']}.png",
            }
            texture_index = len(appearance["textures"])
            appearance["textures"].append(texture)

            texture_indices.insert(0, texture_index)

        return texture_indices

    def construct_texture_maps(
        self,
        geom: Geometry,
        texture_indices: List,
        textures_enabled: bool = False
    ) -> Geometry:
        """
        Construct a texture map to be used
        first index refers to the texture object.
        the of the indices refer to the indices of the vertices-textures indices in the appearance object
        """
        if textures_enabled:
            geom_texture = {
                "cyclomedia": {
                    "values": [
                        [
                            [
                                texture_indices
                            ]
                        ]
                    ]
                }
            }
            geom.texture = geom_texture
            return geom
        return geom
