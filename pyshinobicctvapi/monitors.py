"""
Shinobi API key management
"""

import json
from .entity import Entity
from .manager import Manager as EntityManager
from typing import Dict, Iterable, Optional, List, Type, Mapping, Container, Iterator

from .connection import Connection

ACTION = "monitor"

DEFAULT = {"details": {}}


class Details:
    def __init__(self, details: dict = None):
        if details is None:
            details = {}
        self._details = details


class Stream:
    def __init__(self, base_url: str, url: str, typ: str):
        self._base = base_url
        self._url = url
        self._type = typ

    @property
    def url(self):
        return self._base + self._url

    @property
    def type(self):
        return self._type


class StreamCollection(Iterable[Stream]):
    def __init__(
        self, streams: Dict[str, List[str]], base_url: str = None, typ: str = None
    ):
        self._streams = streams
        self._base_url = base_url
        self._type = typ

    def _iterateType(self, typ: str) -> Iterator[Stream]:
        for stm in self._streams[typ]:
            yield Stream(self._base_url, stm, typ)

    def __iter__(self) -> Iterator[Stream]:
        if self._type is not None:
            for stm in self._iterateType(self._type):
                yield stm
            return

        for typ in self._streams:
            for stm in self._iterateType(typ):
                yield stm

    def __contains__(self, typ):
        if self._type is not None:
            return type == self._type

        return typ in self._streams

    def __getitem__(self, typ):
        if self._type is not None and typ != self._type:
            return
        return self


class TypedStreamCollection(
    StreamCollection, Mapping[str, StreamCollection], Container[str]
):
    def __init__(
        self,
        streams: Dict[str, List[str]],
        order: List[str],
        base_url: str = None,
    ):
        super().__init__(streams, base_url)

    def __len__(self):
        return 0

    def __getitem__(self, typ) -> StreamCollection:
        if typ not in self._streams:
            return None

        return StreamCollection(self._streams, self._base_url, typ)


class Monitor(Entity):
    def __init__(self, data: dict = None, base_url: str = None):
        super().__init__("mid", data)
        self._base_url = base_url

    @property
    def name(self) -> Optional[str]:
        return self._data.get("name")

    @property
    def type(self) -> Optional[str]:
        return self._data.get("type")

    @property
    def ext(self) -> Optional[str]:
        return self._data.get("ext")

    @property
    def protocol(self) -> Optional[str]:
        return self._data.get("protocol")

    @property
    def fps(self) -> Optional[int]:
        return self._data.get("fps")

    @property
    def mode(self) -> Optional[str]:
        return self._data.get("mode")

    @property
    def width(self) -> Optional[int]:
        return self._data.get("width")

    @property
    def height(self) -> Optional[int]:
        return self._data.get("height")

    @property
    def status(self) -> Optional[str]:
        return self._data.get("status")

    @property
    def details(self):
        if not hasattr(self, "_details"):
            self._details = json.loads(self._data.setdefault("details", "{}"))
        return Details(self._details)

    @property
    def snapshot(self) -> Optional[str]:
        snapshot = self._data.get("snapshot")
        if snapshot is None:
            return None
        return self._base_url + snapshot

    @property
    def streams(self) -> TypedStreamCollection:
        return TypedStreamCollection(
            self._data.get("streamsSortedByType", {}),
            self._data.get("streams"),
            self._base_url,
        )


class Manager(EntityManager[Monitor]):
    def __init__(self, connection: Connection):
        super().__init__(connection, ACTION, Monitor)

    async def async_started(self) -> Iterable[Monitor]:
        """
        Get a list of monitors for the current connection
        """
        return map(self._create, await self._async_action_get(f"s{ACTION}"))
