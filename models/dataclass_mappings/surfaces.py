from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapper

import uuid
from typing import List
from dataclasses import dataclass
from geoalchemy2 import Geometry
from enum import Enum

import models
from models.dataclass_mappings.enumType import EnumType
from models.dataclass_mappings.buildings import Building


class Surface_type(Enum):
    GroundSurface = 0
    RoofSurface = 1
    OuterWallSurface = 2
    InnerWallSurface = 3


class Surface(models.BaseTable):
    __tablename__ = 'surfaces'
    __table_args__ = {"schema": models.RESULT_SCHEMA}

    id = Column('id', UUID(), primary_key=True)
    bag_building_id = Column(
        'bag_building_id', String(20),
        ForeignKey(Building.id, ondelete="CASCADE", onupdate="CASCADE")
    )
    semantics_value = Column('semantics_value', EnumType(enum_class=Surface_type))
    surface_geometry = Column('surface_geometry', Geometry(geometry_type='POLYGON'))


@dataclass
class Surface_dataclass:
    id: uuid
    bag_building_id: str
    semantics_value: Surface_type
    surface_geometry: Geometry()

mapper(Surface_dataclass, Surface)
