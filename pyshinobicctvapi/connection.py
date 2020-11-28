import aiohttp

class Connection:
    """
    Client Connection wrapper class to simplify the API calls
    """

    def __init__(self, host: str, port: int = 80, session: aiohttp.ClientSession = None):
        if host[:7].upper() == 'HTTP://':
            host = host[7:]
        elif host[:8].upper() == 'HTTPS://':
            host = host[8:]
            port = 443

        self.host = host
        self.port = port
        self._session = session

    @property
    def base_url(self) -> str:
        """
        Provides a base url for building requests
        """

        return 'http' + ('s' if self.port == 443 else '') + f'://{self.host}' + (f':{self.port}' if self.port != 443 and self.port != 80 else '')

    def action_url(self, action: str, command: str = None) -> str:
        """
        provides an api url for the requested action
        """

        if not self._token or not self._group:
            raise RuntimeError('You must establish a connection before you can make a call.')

        return f'/{self._token}/{action}/{self._group}' + (f'/{command}' if not command is None else '')

    def _init(self, apiKey: str, group: str):
        self._token = apiKey
        self._group = group

    def _ensure_url(self, url: str) -> str:
        if url is None:
            return self.base_url
        if url[0] == '/':
            return self.base_url + url
        if url[:4].upper() != 'HTTP':
            return f'{self.base_url}/{url}'
        return url

    def _ensure_session(self):
        if self._session is None:
            self._ownsSession = True
            self._session = aiohttp.ClientSession()

    def close(self):
        if not self._session is None and self._ownsSession:
            self._ownsSession = False
            self._session.close()
        self._session = None

    async def _raise_for_not_json_ok(self, response: aiohttp.ClientResponse) -> dict:
        json = await response.json()
        if json.get('ok') == False:
            raise RuntimeError(json['msg'])

        return json

    async def get(self, url: str) -> dict:
        """
        Provides a wrapper arounf aiohttp for getting json

        Parameters
        ----------
        url : str
            Url to fetch will be prefixed with base_url if not absolute
        """

        self._ensure_session()
        url = self._ensure_url(url)

        resp = await self._session.get(url)
        resp.raise_for_status()
        return await self._raise_for_not_json_ok(resp)

    async def post(self, url: str, body: dict = None) -> dict:
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

        resp = await self._session.post(url, json=body)
        resp.raise_for_status()
        return await self._raise_for_not_json_ok(resp)
            
