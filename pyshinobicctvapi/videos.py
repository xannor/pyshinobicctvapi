from typing import List

from .connection import Connection

from datetime import datetime

ACTION = "videos"


class Video:
    """
    Shinobi Video API
    """

    def __init__(self, video: dict = None):
        self._video = video or {}


async def async_all(
    connection: Connection, start: datetime = None, end: datetime = None
) -> List[Video]:
    """
    Get a list of videos for the specified connection
    """

    url = connection.action_url(ACTION)
    if start is not None:
        url += "?start=%s" % start.isoformat()

    if end is not None:
        url += ("?" if url.find("?") < 0 else "&") + ("end=%s" % end.isoformat())

    json = await connection.get(url)
    return list(map(Video, json["videos"]))


class Manager:
    def __init__(self, connection: Connection):
        self._connection = connection

    async def all(self, start: datetime = None, end: datetime = None) -> List[Video]:
        """
        Get a list of videos for the current connection
        """

        return async_all(self._connection, start, end)
