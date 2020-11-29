from typing import Optional, TypeVar


T = TypeVar("T", bound="Entity")


class Entity:
    """ Base Shinobi API Entity """

    def __init__(self, key: str, data: dict = None):
        self._key = key
        self._data = data

    @property
    def id(self: T) -> str:
        return self._data[self._key]

    @property
    def group(self: T) -> Optional[str]:
        return self._data.get("ke")