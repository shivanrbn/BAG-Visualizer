
from os import getenv
from typing import List
from shapely.geometry import Point
from uuid import uuid4
from models.dataclass_mappings.bounding_box import BoundingBox
from models.dataclass_mappings.panorama import Panorama_dataclass
from models.dataclass_mappings.image import Streetview_Image_dataclass
import requests
from typing import Union

class StreetviewService:

    def __init__(self) -> None:
        self.googleKey = getenv("streetview_api_key")
        self.cyclomediaKey = getenv("cyclomedia_api_key")
        self.cyclomediaStreetviewBase = 'https://atlas.cyclomedia.com/PanoramaRendering'
        self.cyclomediaAerialBase = ''
        self.auth = requests.auth.HTTPBasicAuth(getenv('cyclomedia_username'), getenv('cyclomedia_password'))

    def renderSurface(self,
                      bbox: BoundingBox
                      ) -> Union[Panorama_dataclass, Streetview_Image_dataclass]:
        """
        RenderSurface api call of cyclomedia

        this renders a surface using the following:
        /RenderSurface/<srs>/<coordinates>/?apiKey=<apiKey>

        upper left,
        upper right, lower right and lower left
        corner, as seen from the observer

        A traffic sign on a Dutch highway:
        https://atlas.cyclomedia.com/PanoramaRendering/RenderSurface/28992/163939.296
        444;379550.768569;32.5940330406;163939.271713;379555.715094;32.5827216870;163939.
        232470;379555.677124;28.1069348311;163939.257536;379550.711447;28.1455324211/?ap
        iKey=<put_your_api_key_here>&maxelevation=65

        Returns a single panorama and image dataclass object
        """
        request_url = (
            f"{self.cyclomediaStreetviewBase}/RenderSurface/28992/"
            + f"{bbox.upper_left.x};{bbox.upper_left.y};{bbox.upper_left.z};"
            + f"{bbox.upper_right.x};{bbox.upper_right.y};{bbox.upper_right.z};"
            + f"{bbox.lower_right.x};{bbox.lower_right.y};{bbox.lower_right.z};"
            + f"{bbox.lower_left.x};{bbox.lower_left.y};{bbox.lower_left.z}/"
        )

        params = {
            "apiKey": self.cyclomediaKey,
            "margin": 0.1
        }
        resp = requests.get(request_url, params=params, auth=self.auth)
        print(resp)
        if resp.status_code == 502:
            raise requests.exceptions.RetryError("got a bad gateway from Cyclomedia")
        if resp.status_code == 400:
            raise requests.exceptions.HTTPError("400 not found error, continuing.")

        image_id = uuid4()

        panorama_recording = Panorama_dataclass(
            id=uuid4(),
            panorama_id=resp.headers["Recording-Id"],
            surface_id=bbox.surface_id,
            recording_location=Point(
                float(resp.headers["RecordingLocation-X"]),
                float(resp.headers["RecordingLocation-Y"]),
                float(resp.headers["RecordingLocation-Z"])
            ).wkt,
            recording_date=resp.headers["Recording-Date"]
        )

        image_recording = Streetview_Image_dataclass(
            id=image_id,
            surface_id=bbox.surface_id,
            panorama_id=resp.headers["Recording-Id"],
            image_width=resp.headers["Render-Width"],
            image_height=resp.headers["Render-Height"],
            image=resp.content
        )

        return panorama_recording, image_recording
