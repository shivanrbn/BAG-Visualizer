import abc
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

Base = declarative_base()


class BaseTable(Base):
    __abstract__ = True

    @abc.abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError('Implement this function')

    @abc.abstractmethod
    def to_wkt(self):
        """
        convert Well Known Binary (WKB) to Well Known Test (WKT) for a shape.
        """
        raise NotImplementedError('Implement this function')


SOURCE_SCHEMA = 'bag3d'
RESULT_SCHEMA = 'data'
