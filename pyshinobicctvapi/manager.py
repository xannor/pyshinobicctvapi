from .entity import Entity
from .connection import Connection

from typing import Iterable, Type, TypeVar, Generic

T = TypeVar("T", bound=Entity)


class Manager(Generic[T]):
    def __init__(
        self, connection: Connection, action: str, constructor: Type[T] = None
    ):
        self._connection = connection
        self._action = action
        self._constructor = constructor

    async def _async_action_get(
        self, action: str = None, command: str = None, property: str = None
    ):
        return await self._connection.get(
            self._connection.action_url(action or self._action, command), property
        )

    def _create(self, data: dict) -> T:
        if self._constructor is None:
            raise NotImplementedError("Not implemented")
        return self._constructor(data=data, base_url=self._connection.base_url)

    async def _async_all(self, *args, **kwargs):
        return await self._async_action_get()

    async def async_all(self, *args, **kwargs) -> Iterable[T]:
        return map(self._create, await self._async_all(*args, **kwargs))

    async def _async_get(self, id: str, *args, **kwargs):
        return await self._async_action_get(command=id)

    async def async_get(self, id: str, *args, **kwargs) -> T:
        return next(map(self._create, await self._async_get(id, *args, **kwargs)))
