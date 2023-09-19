from os import getenv
from uuid import uuid4
import requests
from owslib.wms import WebMapService

from models.dataclass_mappings.bounding_box import BoundingBox
from models.dataclass_mappings.image import Aerial_Image_dataclass


class WMSService:
    """
    This class:
    - Requests a specific tile from WMS
    - Downloads the the tile in the most detailed layer.
    - crops the image to the bounding box of the roofs.

    WMS service supported:
    - Cyclomedia: https://atlas.Cyclomedia.com/geodata/wms
    """

    def __init__(self, srs: int = 28992, layer: str = 'NL_aerial_2021_10cm'):
        self.wms = WebMapService(
            url='https://atlas.Cyclomedia.com/geodata/wms?',
            username=getenv("cyclomedia_username", None),
            password=getenv("cyclomedia_password", None)
        )
        self.srs = srs
        self.layer = layer
        self.width = 4096
        self.height = 4096

        self.auth = requests.auth.HTTPBasicAuth(getenv('cyclomedia_username'), getenv('cyclomedia_password'))

    def request_image(
        self,
        bbox: BoundingBox,
    ) -> Aerial_Image_dataclass:
        """
        Requests an image with the supplied params
        the srs = 28992 as the srs of the database geometries in the project.
        the bounding_box is 4 points in lat/lon points.
        """
        parameter_srs = f"EPSG:{self.srs}"
        parameter_format = "image/tiff"

        image = self.wms.getmap(
            layers=[self.layer],
            srs=parameter_srs,
            format=parameter_format,
            bbox=(
                bbox.lower_left.x,
                bbox.lower_left.y,
                bbox.upper_right.x,
                bbox.upper_right.y
            ),
            size=(self.height, self.width)
        )

        return Aerial_Image_dataclass(
            id=uuid4(),
            surface_id=bbox.surface_id,
            image_height=self.height,
            image_width=self.width,
            image=image.read()
        )
