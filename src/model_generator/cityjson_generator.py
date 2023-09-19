import numpy as np
import os
import io
from PIL import Image
import shutil
from cjio import cityjson
from cjio.models import CityObject, Geometry
from typing import Dict, List
from shapely.geometry import Point, Polygon

from src.model_generator.model_generator import ModelGenerator
from src.polygon_calculator.uv_calculator import UVCalculator

from models.dataclass_mappings.buildings import Building_dataclass
from models.dataclass_mappings.surfaces import Surface_dataclass, Surface_type


class CityJSONGenerator(ModelGenerator):
    """
    For now this class only generates cityJSON files.
    it holds a vertex pointer in the store function
    to keep track of the array indices when constructing the textures.
    """

    def __init__(self):
        super().__init__()

    def generate(
        self,
        building: Building_dataclass,
        textures_enabled: bool = False
    ) -> None:
        """
         Example of an empty CityJSON file:
        {
            "type": "CityJSON",
            "version": "1.0",
            "extensions": {},
            "transform": {
                "scale": [0.0, 0.0, 0.0],
                "translate": [1.0, 1.0, 1.0]
            },
            "metadata": {
                "referenceSystem": "https://www.opengis.net/def/crs/EPSG/0/4326"
            }
            "CityObjects": {},
            "vertices": [],
            "appearance": {},
            "geometry-templates": {}
        }
        """

        uv_calculator = UVCalculator(building_id=building.id)

        appearance = self._construct_base_appearance(textures_enabled=textures_enabled)
        # appearance can't be assigned directly?
        # only loaded from j in constructor, so adding this to the wonky api myself
        template = self._construct_template(
            building=building,
        )
        cm = cityjson.CityJSON(j=template)
        cm.is_transformed = True
        cm.j["appearance"] = appearance

        # parent building and geom
        parent_building = CityObject(
            id=building.id,
            type='Building',
        )
        transformed_building = self._normalize_geometries(
            building=building,
            translation_coordinates=template["transform"]
        )

        surface_indices = self._extract_boundaries(building=transformed_building)

        # list indices are boundary indices
        for boundary in surface_indices:
            co = CityObject(
                id=surface_indices[boundary]["id"],
                type='BuildingPart',
                parents=[parent_building.id]
            )
            boundaries = []
            boundaries.append([point for point in surface_indices[boundary]['surface']])

            # construct a base geometry
            geom = Geometry(type='Solid', lod="2.2")
            geom.boundaries.append(boundaries)

            if surface_indices[boundary]["type"] == "WallSurface":
                geom.surfaces[0] = {"surface_idx": [[0, 0]], "type": "WallSurface"}
            if surface_indices[boundary]["type"] == "GroundSurface":
                geom.surfaces[0] = {"surface_idx": [[0, 0]], "type": "GroundSurface"}
            if surface_indices[boundary]["type"] == "RoofSurface":
                geom.surfaces[0] = {"surface_idx": [[0, 0]], "type": "RoofSurface"}

            # first add uv vertices to the vertices-texture object
            texture_indices = uv_calculator.map_uv_appearance(
                surface=surface_indices[boundary],
                appearance=appearance,
                textures_enabled=textures_enabled
            )

            # then append to the geom object of the building_part:
            geom = uv_calculator.construct_texture_maps(
                geom=geom,
                texture_indices=texture_indices,
                textures_enabled=textures_enabled
            )
            co.geometry.append(geom)

            # append to main city object
            parent_building.children.append(co.id)
            cm.cityobjects[co.id] = co

        cm.cityobjects[parent_building.id] = parent_building
        return cm

    
    def save(
        self,
        building: Building_dataclass,
        images: List,
        cm: cityjson.CityJSON,
        filename: str
    ) -> None:
        # save the building and their images
        dir = building.id
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)

        cityjson.save(cm, f"{dir}/{filename}.json")

        for image in images:
            img = Image.open(io.BytesIO(image.image))
            img.save(f"{dir}/{image.surface_id}.png")
        print("wrote to file")

    def _construct_template(
        self,
        building: Building_dataclass,
    ) -> dict:

        geographical_bbox = self._construct_geographical_extent(building)
        return {
            "type": "CityJSON",
            "version": "1.1",
            "metadata": {
                    "referenceSystem": "https://www.opengis.net/def/crs/EPSG/0/28992",
                    "geographicalExtent": geographical_bbox
            },
            "CityObjects": {},
            "vertices": [],
            "transform": self._get_translation(building=building)["transform"],
            "appearance": {}
        }

    def _get_translation(self, building: Building_dataclass) -> Dict:
        """
        Get a minimum translation to scale down the coordinates
        from the groundsurface.

        Most buildings only have 1 groundsurface,
        so take that as a rule of thumb.
        return this as a dict for CityJSON generation.
        """
        for surface in building.surfaces:
            if surface.semantics_value == Surface_type.GroundSurface:
                x, y = surface.surface_geometry.exterior.coords.xy
                x_min = min(x)
                y_min = min(y)
        return {
            "transform": {
                "scale": [0.01, 0.01, 0.01],
                "translate": [x_min, y_min, 0.0]
            }
        }

    def _construct_geographical_extent(self, building: Building_dataclass) -> dict:
        """
        Create one big polygon for the building to use as a geographical extent
        """
        building_polygon = np.empty([0, 3])
        for surface in building.surfaces:
            exterior = np.array([point for point in surface.surface_geometry.exterior.coords])
            building_polygon = np.vstack([building_polygon, exterior])
        building_polygon = Polygon(building_polygon)

        x, y = building_polygon.exterior.coords.xy
        x_min = np.min(x)
        y_min = np.min(y)
        x_max = np.max(x)
        y_max = np.max(y)
        z_min = np.min([point[2] for point in building_polygon.exterior.coords])
        z_max = np.max([point[2] for point in building_polygon.exterior.coords])

        return [x_min, y_min, z_min, x_max, y_max, z_max]

    def _extract_boundaries(self, building: Building_dataclass) -> Dict:
        """
        Extract the boundaries and put them in a layered dictionary, construct a 2d array from this dictionary
        """
        surface_indices = {}
        for index, surface in enumerate(building.surfaces):
            surface_indices[index] = {
                "id": surface.id,
                "surface": [[(round(coord[0]), round(coord[1]), round(coord[2])) for coord in surface.surface_geometry.exterior.coords]],
                "type": self._construct_types(surface.semantics_value)
            }
        return surface_indices

    def _construct_types(self, surface_type: Surface_dataclass.semantics_value) -> str:
        """
        Per cityJSON/cityGML standard
        """
        if surface_type == Surface_type.GroundSurface:
            return "GroundSurface"
        elif surface_type == Surface_type.OuterWallSurface or surface_type == Surface_type.InnerWallSurface:
            return "WallSurface"
        else:
            return 'RoofSurface'

    def _normalize_geometries(self, building: Building_dataclass, translation_coordinates: Dict) -> Building_dataclass:
        """
        extract the translation coordinates from the geometries
        and normalizes the geometries using the transform component.
        """
        for surface in building.surfaces:

            _new_coords = []
            for coord in surface.surface_geometry.exterior.coords:
                _new_coords.append(
                    Point(
                        round((coord[0] - translation_coordinates["translate"][0]) / translation_coordinates["scale"][0], 0),
                        round((coord[1] - translation_coordinates["translate"][1]) / translation_coordinates["scale"][1], 0),
                        round(coord[2] / translation_coordinates["scale"][2], 0)))
            surface.surface_geometry = Polygon(_new_coords)
        return building

    def _construct_base_appearance(self, textures_enabled: bool = False) -> Dict:
        appearance = {}
        if textures_enabled:
            appearance["textures"] = []
            appearance["vertices-texture"] = []

        return appearance
