from abc import ABC
from dataclasses import dataclass, field
from geoalchemy2 import Geometry
from typing import List
import uuid

from sqlalchemy import ForeignKey, MetaData, Column
from sqlalchemy.types import String, Integer, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm.mapper import Mapper


import models
from models.dataclass_mappings.surfaces import Surface

metadata = MetaData()


@dataclass
class Image_dataclass(ABC):
    id: uuid
    image_width: int = 0
    image_height: int = 0
    image: bytes = field(default_factory=List)

@dataclass
class Streetview_Image_dataclass(Image_dataclass):
    panorama_id: str = None
    surface_id: uuid = None

@dataclass
class Aerial_Image_dataclass(Image_dataclass):
    surface_id: uuid = None

class Image(models.BaseTable):
    __abstract__ = True

    id = Column("id", UUID(as_uuid=True), primary_key=True)
    image_width = Column("image_width", Integer())
    image_height = Column("image_height", Integer())
    image = Column("image", LargeBinary())

class StreetviewImage(Image, models.BaseTable):
    __tablename__ = 'cyclomedia_streetview_images'
    __table_args__ = {"schema": models.RESULT_SCHEMA}

    panorama_id = Column("panorama_id", String(), primary_key=True)
    surface_id = Column(
        'surface_id', UUID(as_uuid=True),
        ForeignKey(Surface.id, ondelete="CASCADE", onupdate="CASCADE")
    )


Mapper(Streetview_Image_dataclass, StreetviewImage)


class AerialImage(Image, models.BaseTable):
    __tablename__ = 'cyclomedia_aerial_image'
    __table_args__ = {"schema": models.RESULT_SCHEMA}

    surface_id = Column(
        'surface_id', String(),
        ForeignKey(Surface.id, ondelete="CASCADE", onupdate="CASCADE")
    )

Mapper(Aerial_Image_dataclass, AerialImage)
