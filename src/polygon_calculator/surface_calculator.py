
from typing import Dict, List

from rasterio import MemoryFile
from rasterio.mask import mask

import numpy as np
from shapely import geometry
from shapely.affinity import rotate
import logging

from src.polygon_calculator.calculator import Calculator
from models.dataclass_mappings.surfaces import Surface_type, Surface_dataclass
from models.dataclass_mappings.bounding_box import BoundingBox
from models.dataclass_mappings.buildings import Building_dataclass
from models.dataclass_mappings.image import Aerial_Image_dataclass


class SurfaceCalculator(Calculator):

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def calculate_surface_bounding_boxes(self, building: Building_dataclass) -> List:
        """
        creates a list of bounding boxes.
        """
        outer_wall_bbox_list = []
        roof_bbox_list = []
        for surface in building.surfaces:
            if surface.semantics_value == Surface_type.OuterWallSurface:
                outer_wall_bbox_list.append(self._create_bounding_box(surface))
            elif surface.semantics_value == Surface_type.RoofSurface:
                roof_bbox_list.append(self._create_bounding_box(surface))
        return outer_wall_bbox_list, roof_bbox_list

    def process_roof_images(
        self,
        building: Building_dataclass,
        images: List
    ) -> Aerial_Image_dataclass:
        """
        Supplied with a building and a list of images do the following:
        - find the matching surfaces with the image
        - crops the images and put them in a new dataclass.
        """

        cropped_images = []
        roof_surfaces = [
            surface for surface in building.surfaces if surface.semantics_value == Surface_type.RoofSurface
        ]
        for roof_surface in roof_surfaces:
            for image in images:
                if image.surface_id == roof_surface.id:
                    cropped_images.append(self._crop_roof_image(surface=roof_surface, image=image))
        return cropped_images

    def _create_bounding_box(self, surface: Surface_dataclass) -> BoundingBox:
        """
        Creates a bounding box in the format
        Upper left  : x:y:z
        Upper right : x:y:z
        Lower right : x:y:z
        Lower Left  : x:y:z

        Get the convex hull for each surface (exterior) for each surface
        for walls: use relative coordinates, the corner points are defined you facing against a wall.
        for roofs: use the original polygon,since it's top-down perspective
        """

        polygon_surface = geometry.Polygon()
        if surface.semantics_value == Surface_type.OuterWallSurface:
            first_point = surface.surface_geometry.exterior.coords[0]
            last_point = surface.surface_geometry.exterior.coords[-2]

            degrees = self._get_azimuth(first_point, last_point)
            rotated_wall = self._rotate_wall(
                wall=surface.surface_geometry,
                degrees=degrees,
                required_angle=45
            )

            first_rotated_point = rotated_wall.exterior.coords[0]
            polygon_surface = geometry.Polygon(
                np.subtract(rotated_wall.exterior.coords, first_rotated_point)
            )
        else:
            polygon_surface = surface.surface_geometry

        argmin, argmax = self._get_min_max_indices(polygon_surface)
        bbox = BoundingBox(
            surface_id=surface.id,
            upper_left=geometry.Point(
                surface.surface_geometry.exterior.coords[argmin[0]][0],
                surface.surface_geometry.exterior.coords[argmin[1]][1],
                surface.surface_geometry.exterior.coords[argmax[2]][2]
            ),
            lower_left=geometry.Point(
                surface.surface_geometry.exterior.coords[argmin[0]][0],
                surface.surface_geometry.exterior.coords[argmin[1]][1],
                surface.surface_geometry.exterior.coords[argmin[2]][2]
            ),
            lower_right=geometry.Point(
                surface.surface_geometry.exterior.coords[argmax[0]][0],
                surface.surface_geometry.exterior.coords[argmax[1]][1],
                surface.surface_geometry.exterior.coords[argmin[2]][2],
            ),
            upper_right=geometry.Point(
                surface.surface_geometry.exterior.coords[argmax[0]][0],
                surface.surface_geometry.exterior.coords[argmax[1]][1],
                surface.surface_geometry.exterior.coords[argmax[2]][2]
            )
        )

        return bbox

    def _crop_roof_image(
        self,
        surface: Surface_dataclass,
        image: Aerial_Image_dataclass
    ) -> Aerial_Image_dataclass:

        # TODO do some error handling here
        # we just need lat/lon coordinates, z-coordinates can be left out.
        poly = geometry.Polygon([(point[0], point[1]) for point in surface.surface_geometry.exterior.coords])

        # opens as read-only
        with MemoryFile(file_or_bytes=image.image, ext='tiff') as memfile:
            with memfile.open() as dataset:
                cropped_image_array, cropped_transform = mask(dataset=dataset, shapes=[poly], nodata=0, crop=True)
                cropped_metadata = dataset.meta
                print(cropped_image_array.shape)

            cropped_metadata.update(
                {
                    "driver": "PNG",
                    "height": cropped_image_array.shape[1],
                    "width": cropped_image_array.shape[2],
                    "transform": cropped_transform
                }
            )

        # we write the output to a new empty memoryfile
        with MemoryFile() as memfile2:
            with memfile2.open(**cropped_metadata) as dataset:
                dataset.write(cropped_image_array)

            masked_image = memfile2.read()

        return Aerial_Image_dataclass(
            id=image.id,
            surface_id=surface.id,
            image_height=image.image_height,
            image_width=image.image_width,
            image=masked_image
        )
