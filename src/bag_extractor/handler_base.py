from abc import ABC, abstractmethod
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import NullPool
from os import getenv
from dotenv import load_dotenv
from models import BaseTable


class Collector(ABC):

    def __init__(self) -> None:
        self.session_factory = SessionHandler()

        # set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s-%(threadName)s: %(message)s'
        )
    @abstractmethod
    def _collect_surfaces(self, bag_building_id: str):
        raise NotImplementedError('Implement this')

    @abstractmethod
    def _collect_images(self, model: BaseTable):
        raise NotImplementedError('Implement this')
    

class SessionHandler:
    engine = None

    def __init__(self, echo=False):
        load_dotenv()

        user = getenv('user')
        host = getenv('host')
        name = getenv('dbname')
        self.engine = create_engine(
            f'postgresql://{user}:@{host}/{name}',
            poolclass=NullPool,
            echo=echo
        )

    def build(self) -> Session:
        return sessionmaker(bind=self.engine)()
