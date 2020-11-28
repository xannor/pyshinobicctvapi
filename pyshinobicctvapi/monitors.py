"""
Shinobi API key management
"""

from typing import Optional, List

from connection import Connection

ACTION='monitor'

DEFAULT = {
    "details": {
    }
}

class Manager:
    def __init__(self, connection: Connection):
        self._connection = connection

    async def all(self) -> List[Monitor]:
        """
        Get a list of monitors for the current connection
        """

        json = await self._connection.get(self._connection.action_url(ACTION))
        return list(map(Monitor), json['list'])

    async def started(self) -> List[Monitor]:
        """
        Get a list of monitors for the current connection
        """

        json = await self._connection.get(self._connection.action_url(f's{ACTION}'))
        return list(map(Monitor), json['list'])

class Details:

    def __init__(self, details: dict = None):
        if details is None:
            details = {}
        self._details = details

class Monitor:

    def __init__(self, monitor: dict = None):
        self._monitor = monitor

    @property
    def name(self) -> Optional[str]:
        return self._monitor.get('name')

    @property
    def type(self) -> Optional[str]:
        return self._monitor.get('type')

    @property
    def ext(self) -> Optional[str]:
        return self._monitor.get('ext')

    @property
    def protocol(self) -> Optional[str]:
        return self._monitor.get('protocol')

    @property
    def fps(self) -> Optional[int]:
        return self._monitor.get('fps')

    @property
    def mode(self) -> Optional[str]:
        return self._monitor.get('mode')

    @property
    def width(self) -> Optional[int]:
        return self._monitor.get('width')

    @property
    def height(self) -> Optional[int]:
        return self._monitor.get('height')

    @property
    def status(self) -> Optional[str]:
        return self._monitor.get('status')

    @property
    def details(self):
        return Details(self._monitor.setdefault('details', {}))

    @property
    def snapshot(self) -> Optional[str]:
        return self._monitor.get('snapshot')

    @property
    def streams(self) -> List[str]:
        return self._monitor.get('streams', [])
