from abc import ABC, abstractmethod


class ModelGenerator(ABC):
    """
    Small stubs for now.
    """

    def __init__(self):
        pass

    @abstractmethod
    def save(self):
        raise NotImplementedError("Implement this")

    def generate(self):
        raise NotImplementedError("Implement this")
