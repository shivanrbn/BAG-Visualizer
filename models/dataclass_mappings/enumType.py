from __future__ import print_function, division, absolute_import
from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator


class EnumType(TypeDecorator):
    """Store IntEnum as Integer"""

    impl = Integer

    def __init__(self, *args, **kwargs):
        self.enum_class = kwargs.pop('enum_class')
        self.cache_ok = True
        TypeDecorator.__init__(self, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, self.enum_class):
                raise TypeError("Value should %s type" % self.enum_class)
            return value.value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, int):
                raise TypeError(f"value is {type(value)}, but should have should have int type")
            return self.enum_class(value)
