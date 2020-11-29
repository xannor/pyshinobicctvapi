import aiohttp
from typing import Callable, Optional
from uuid import uuid1
from yarl import URL

from . import errors


def base_url(info: dict) -> str:
    """
    Provides a base url for building requests
    """
    url = "http"
    port = info.get("port")
    if port == 443:
        url += "s"
    url += f"://{info['host']}"
    if port and port != 443 and port != 80:
        url += f":{port}"

    return url


def action_url(info: dict, action: str, command: str = None) -> str:
    """
    provides an api url for the requested action
    """
    token = info.get("token")
    group = info.get("group")

    if action is None or token is None or group is None:
        return ""

    url = f"/{token}/{action}/{group}"
    if command is not None:
        url += f"/{command}"

    return url


class Info:
    """
    Connection Information
    """

    def __init__(self, info: dict = None):
        self._info = info

    @property
    def host(self) -> str:
        return self._info["host"]

    @property
    def port(self) -> Optional[int]:
        return self._info.get("port")

    @property
    def group(self) -> Optional[str]:
        return self._info.get("group")

    @property
    def base_url(self) -> str:
        """
        Provides a base url for building requests
        """
        return base_url(self._info)

    def action_url(self, action: str, command: str = None) -> str:
        """
        provides an api url for the requested action
        """
        return action_url(self._info, action, command)


class Connection:
    """
    Client Connection wrapper class to simplify the API calls
    """

    def __init__(
        self,
        host: str,
        port: int = 80,
        apiKey: str = None,
        group: str = None,
        session: aiohttp.ClientSession = None,
    ):
        if host[:7].upper() == "HTTP://":
            host = host[7:]
        elif host[:8].upper() == "HTTPS://":
            host = host[8:]
            port = 443

        self._info = {"host": host}
        if port is not None:
            self._info["port"] = port
        if apiKey is not None:
            self._info["token"] = apiKey
        if group is not None:
            self._info["group"] = group
        self._ownsSession = False
        self._session = session

    @property
    def info(self):
        return Info(self._info)

    @property
    def base_url(self) -> str:
        """
        Provides a base url for building requests
        """
        return base_url(self._info)

    def action_url(self, action: str, command: str = None):
        """
        provides an api url for the requested action
        """

        url = action_url(self._info, action, command)
        if url == base_url(self._info):
            raise RuntimeError(
                "You must establish a connection before you can make a call."
            )

        return url

    async def login(self, email: str, password: str, authKey: Callable[[], str] = None):
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
        if "token" in self._info and "group" in self._info:
            return self

        await self._ssl_check()

        body = {"mail": email, "pass": password}

        if not authKey is None:
            body["machineID"] = uuid1()

        try:
            user = await self.post("?json=true", body, "$user")
        except errors.NotOk:
            raise errors.Unauthorized

        self._info["token"] = user["auth_token"]
        self._info["group"] = user["ke"]
        return self

    def _ensure_url(self, url: str) -> str:
        if url is None:
            return self.base_url
        if url[0] == "/":
            return self.base_url + url
        if url[:4].upper() != "HTTP":
            return f"{self.base_url}/{url}"
        return url

    def _ensure_session(self):
        if self._session is None:
            self._ownsSession = True
            self._session = aiohttp.ClientSession()

    def _ssl_test(self, resp: aiohttp.ClientResponse):
        if "port" in self._info:
            return

        if resp.status == 301 or resp.status == 302:
            url = URL(resp.headers.get("Location"))
        else:
            url = resp.url

        if url.port is not None:
            self._info["port"] = url.port
        elif url.scheme == "https":
            self._info["port"] = 443
        else:
            self._info["port"] = 80

    async def _ssl_check(self):
        if "port" in self._info:
            return

        self._ensure_session()
        resp = await self._session.head(self.base_url)
        async with resp:
            resp.raise_for_status()
            self._ssl_test(resp)

    def close(self):
        if not self._session is None and self._ownsSession:
            self._ownsSession = False
            self._session.close()

        self._session = None

    async def _raise_for_not_json_ok(
        self, response: aiohttp.ClientResponse, property: str = None
    ):
        json = await response.json()
        if property is not None and property in json:
            json = json[property]

        if json.get("ok") == False:
            raise errors.NotOk(json.get("msg"))

        json.pop("ok", None)

        return json

    async def get(self, url: str, property: str = None):
        """
        Provides a wrapper arounf aiohttp for getting json

        Parameters
        ----------
        url : str
            Url to fetch will be prefixed with base_url if not absolute
        """

        self._ensure_session()
        url = self._ensure_url(url)
        headers = {"Accept": "application/json"}

        resp = await self._session.get(url, headers=headers)
        async with resp:
            resp.raise_for_status()
            self._ssl_test(resp)
            json = await resp.json()
            if property is not None:
                return json.get(property)
            return json

    async def post(self, url: str, body: dict = None, property: str = None):
        """
        Provides a wrapper around aiohttp for posting json

        Parameters
        ----------
        url : str
            Url to fetch will be prefixed with base_url if not absolute
        body : dict
            JSON to post
        """

        self._ensure_session()
        url = self._ensure_url(url)
        headers = {"Accept": "application/json"}

        resp = await self._session.post(url, json=body, headers=headers)
        async with resp:
            resp.raise_for_status()
            self._ssl_test(resp)
            return await self._raise_for_not_json_ok(resp, property)

    async def __aenter__(self):
        self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close()
