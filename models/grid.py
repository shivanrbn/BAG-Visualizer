from typing import List

from sqlalchemy import Column, String, Integer, SmallInteger
import sqlalchemy.types as types
from sqlalchemy.ext.hybrid import hybrid_method
from geoalchemy2 import Geometry, functions

import models


class Grid(models.Base):
    __tablename__ = 'grid'
    __table_args__ = {"schema": models.SOURCE_SCHEMA}

    fid = Column("fid", Integer(), primary_key=True)
    identificatie = Column("identificatie", String(30))
    oorspronkelijk_bouwjaar = Column("oorspronkelijk_bouwjaar",SmallInteger())
    geometrie = Column("geometrie", Geometry())


    @hybrid_method
    def to_wkt(self):
        """
        convert Well Known Binary (WKB) to Well Known Test (WKT)
        """
        return functions.ST_AsText(self.geometrie)