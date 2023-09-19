from time import sleep
from typing import List, Union
from concurrent.futures import ProcessPoolExecutor
from requests.exceptions import HTTPError, RetryError

from src.image_extractor.streetviewservice.streetview_service import StreetviewService
from src.image_extractor.wmsservice.wmsservice import WMSService

from models.dataclass_mappings.bounding_box import BoundingBox
from models.dataclass_mappings.image import Aerial_Image_dataclass, Streetview_Image_dataclass
from models.dataclass_mappings.panorama import Panorama_dataclass


class ImageCollector:
    """
    This class calculates the best position to download an image from
    and also downloads the images and stores them on s3/the database.
    """

    def __init__(self) -> None:
        self.streetviewService = StreetviewService()
        self.wmsService = WMSService()

    def collect_images(
        self,
        outer_wall_bboxes: List,
        roof_bboxes: List,
        workers: int = 5,
    ) -> Union[List, List, List]:
        """
        Iterates through the bounding boxes and sends a request to {api}
        to get an image or metadata

        available API's in this code at the moment:
        - Cyclomedia Streetview
        - Cyclomedia WMS
        """

        panoramas = []
        streetview_images = []

        with ProcessPoolExecutor(max_workers=workers) as streetview_pool:
            streetview_pool_results = streetview_pool.map(self._get_streetview_images, outer_wall_bboxes)

        with ProcessPoolExecutor(max_workers=workers) as streetview_pool:
            aerial_images = streetview_pool.map(self._get_aerial_images, roof_bboxes)

        panorama_recording: Panorama_dataclass
        streetview_image_recording: Streetview_Image_dataclass

        # since we return a union, we need to split the results.
        for panorama_recording, streetview_image_recording in streetview_pool_results:
            panoramas.append(panorama_recording)
            streetview_images.append(streetview_image_recording)

        return panoramas, streetview_images, list(aerial_images)

    def _get_streetview_images(
        self,
        bbox: BoundingBox
    ) -> Union[Panorama_dataclass, Streetview_Image_dataclass]:
        bbox: BoundingBox
        attempt = 0

        for attempt in range(3):
            try:
                print(bbox.surface_id, attempt)
                panorama_recording, image_recording = self.streetviewService.renderSurface(bbox)

            except RetryError as e:
                print(e)
                attempt += 1
                continue
            except HTTPError as e:
                print(e)
                return
            else:
                sleep(1)
                return panorama_recording, image_recording

    def _get_aerial_images(
        self,
        bbox: BoundingBox
    ) -> Aerial_Image_dataclass:
        for attempt in range(3):
            try:
                print(bbox.surface_id, attempt)
                aerial_image = self.wmsService.request_image(bbox)

            except RetryError as e:
                print(e)
                attempt += 1
                continue
            except HTTPError as e:
                print(e)
                return
            else:
                sleep(1)
                return aerial_image
