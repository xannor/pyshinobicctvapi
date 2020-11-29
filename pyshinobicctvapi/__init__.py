from .connection import Connection
from .api import Manager as ApiManager
from .monitors import Manager as MonitorManager
from .videos import Manager as VideoManager


class Client:
    """
    Shinobi API Client

    """

    def __init__(self, connection: Connection):
        self._connection = connection
        self._api: ApiManager = None
        self._monitors: MonitorManager = None
        self._videos: VideoManager = None

    @property
    def api(self):
        if self._api is None:
            self._api = ApiManager(self._connection)
        return self._api

    @property
    def monitors(self):
        if self._monitors is None:
            self._monitors = MonitorManager(self._connection)
        return self._monitors

    @property
    def videos(self):
        if self._videos is None:
            self._videos = VideoManager(self._connection)
        return self._videos

    @property
    def connection(self):
        return self._connection

    def close(self):
        self._connection.close()
