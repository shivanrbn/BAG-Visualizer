from dataclasses import dataclass, field
from typing import List
import uuid
from sqlalchemy import MetaData, Column, ForeignKey
from sqlalchemy.types import String, Date
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.orm import mapper
import models

from models.dataclass_mappings.image import StreetviewImage

metadata = MetaData()


class Panorama(models.BaseTable):
    __tablename__ = 'cyclomedia_streetview_panorama'
    __table_args__ = {"schema": models.RESULT_SCHEMA}

    id = Column("id", UUID(as_uuid=True), primary_key=True)
    panorama_id = Column(
        'panorama_id', String(),
        ForeignKey(StreetviewImage.panorama_id, ondelete="CASCADE", onupdate="CASCADE")
    )
    surface_id = Column('surface_id', UUID(as_uuid=True))
    recording_location = Column("recording_location", Geometry(geometry_type='POINT'))
    recording_date = Column("recording_date", Date())


@dataclass
class Panorama_dataclass:
    id: uuid
    panorama_id: str
    surface_id: uuid
    recording_location: Geometry
    recording_date: str = None


mapper(Panorama_dataclass, Panorama)
