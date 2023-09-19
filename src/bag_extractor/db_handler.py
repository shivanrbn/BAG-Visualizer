import sys
from typing import List, Union

from src.bag_extractor.handler_base import Collector
from psycopg2.errors import NoDataFound
from geoalchemy2.shape import to_shape


from models.dataclass_mappings.surfaces import Surface_dataclass
from models.dataclass_mappings.buildings import Building_dataclass
from models.dataclass_mappings.image import Image, StreetviewImage, AerialImage
class BagCollector(Collector):

    def collect_building(self, bag_building_id):
        """
        Queries from the data.buildings table to get the correct surfaces
        1. check if building exists, if so query the building
        2. query all surfaces of the building, add it to the dataclass
        3. return result as one building dataclass
        """
        try:
            building = self._collect_single_building(bag_building_id)
            building.surfaces = self._collect_surfaces(bag_building_id)
            self._transform_to_wkt(building=building)
            return building
        except NoDataFound as e:
            self.logger.warning(e)
            sys.exit(0)
        except RuntimeError as e:
            self.logger.warning(e)
            sys.exit(1)


    def collect_images(self, bag_building_id) -> Union[List, List]:
        try:
            surface_ids = [id[0] for id in self._collect_surface_ids(bag_building_id)]
            streetview_images = self._collect_images(surface_ids, StreetviewImage)
            aerial_images = self._collect_images(surface_ids, AerialImage)
            return streetview_images, aerial_images
        except NoDataFound as e:
            self.logger.warning(e)
            sys.exit(0)
        except RuntimeError as e:
            self.logger.warning(e)
            sys.exit(1)

    # TODO: caveat: no checks with duplicate when bulk_saving
    def store_streetview(
        self,
        panorama_recordings: List,
        streetview_image_recordings: List
    ) -> None:

        with self.session_factory.build() as session:
            try:
                self.logger.info("Inserting streetview images into db")
                session.bulk_save_objects(streetview_image_recordings)
                self.logger.info("Inserting streetview panorama's into db")
                session.bulk_save_objects(panorama_recordings)
                session.commit()
            except Exception as e:
                self.logger.error("Error bulk inserting in db")
                self.logger.error(e)
                session.rollback()

    # TODO: caveat: no checks with duplicate when bulk_saving
    def store_aerial(self, cropped_roof_images: List) -> None:

        with self.session_factory.build() as session:
            try:
                self.logger.info("Inserting cropped aerial images into db")
                session.bulk_save_objects(cropped_roof_images)
                session.commit()
            except Exception as e:
                self.logger.error("Error bulk inserting in db")
                self.logger.error(e)
                session.rollback()

    def _collect_single_building(self, bag_building_id: str = None):
        with self.session_factory.build() as session:
            query = session.query(Building_dataclass)
            query = query.where(bag_building_id == Building_dataclass.id)
            res = query.all()
            if not res:
                raise NoDataFound("Bag building id not found!")
            return res[0]
    
    def _collect_surfaces(self, bag_building_id: str = None):
        """
        returns all surfaces belonging to a building
        """
        with self.session_factory.build() as session:
            query = session.query(Surface_dataclass)
            query = query.where(bag_building_id == Surface_dataclass.bag_building_id)
            res = query.all()
            if not res:
                raise NoDataFound("surface ids with specified bag building id not found!")
            return res
    
    def _collect_surface_ids(self, bag_building_id: str = None):
        """
        returns all surfaces belonging to a building
        """
        with self.session_factory.build() as session:
            query = session.query(Surface_dataclass.id)
            query = query.where(bag_building_id == Surface_dataclass.bag_building_id)
            res = query.all()
            if not res:
                raise NoDataFound("surface ids with specified bag building id not found!")
            return res
    

    def _collect_images(self, surface_ids: List, model: Image):
        with self.session_factory.build() as session:
            query = session.query(model)
            query = query.filter(model.surface_id.in_(surface_ids))
            res = query.all()
            if not res:
                raise NoDataFound("image ids with specified bag building id not found!")
            return res
    

    def _transform_to_wkt(self, building: Building_dataclass) -> None:
        for surface in building.surfaces:
            surface.surface_geometry = to_shape(surface.surface_geometry)