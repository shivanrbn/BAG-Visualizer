from dataclasses import dataclass
from typing import List
from sqlalchemy import MetaData, Column, String
from sqlalchemy.orm import mapper
from geoalchemy2 import Geometry
import models

metadata = MetaData()


class Building(models.BaseTable):
    __tablename__ = 'buildings'
    __table_args__ = {"schema": models.RESULT_SCHEMA}
    __mapper_args__ = {
        'include_properties': ['id']
    }

    id = Column('id', String(), primary_key=True)
    geometry = Column('geometry', Geometry())


@dataclass
class Building_dataclass:
    id: str = ''
    surfaces: List[dataclass] = None


mapper(Building_dataclass, Building)
