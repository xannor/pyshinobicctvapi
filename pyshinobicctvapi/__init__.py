from typing import Callable
from uuid import uuid1
from .connection import Connection
from .api import Manager as ApiManager
from .monitors import Manager as MonitorManager

class Client:
    """
    Shinobi API Client

    """

    def __init__(self, connection: Connection, apiKey: str, group: str):
        self._connection = connection
        connection._init(apiKey, group)
        self._api = ApiManager(connection)
        self._monitors = MonitorManager(connection)

    @property
    def api(self):
        return self._api

    @property
    def monitors(self):
        return self._monitors

    @property
    def connection(self):
        return self._connection

    def close(self):
        self._connection.close()

    @classmethod
    async def login(cls, connection: Connection, email: str, password: str, authKey: Callable[[], str]):
        """
        Load user information via login

        Parameters
        ----------
        connection : Connection
            The connection object to use
        email : str
            Email address of the user
        password : str
            Password of the user
        authKey : async def callback() -> str (optional)
            Callback to method to retrive two factor response from user if enabled in Shinobi
        """

        body = {
            "mail": email,
            "pass": password
        }

        if not authKey is None:
            body['machineID'] = uuid1()

        json = await connection.post('?json=true', body)
        # TODO : detect two factor and process
        user = json['$user']

        return cls(connection, user['auth_token'], user['ke'])

        