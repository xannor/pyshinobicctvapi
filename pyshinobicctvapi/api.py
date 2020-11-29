"""
Shinobi API key management
"""

from typing import Optional, List, Union

from .connection import Connection

ACTION = "api"

DEFAULT = {
    "ip": "0.0.0.0",
    "details": {
        "auth_socket": "0",
        "control_monitors": "1",
        "delete_videos": "1",
        "get_logs": "1",
        "get_monitors": "1",
        "watch_snapshot": "1",
        "watch_stream": "1",
        "watch_videos": "1",
    },
}


class Details:
    def __init__(self, details: dict = None):
        if details is None:
            details = DEFAULT["details"].copy()
        self._details = details

    @property
    def auth_socket(self) -> bool:
        return (
            self._details.setdefault(
                "auth_socket", DEFAULT["details"].get("auth_socket")
            )
            == "1"
        )

    @auth_socket.setter
    def auth_socket(self, value: bool):
        self._details["auth_socket"] = "1" if value else "0"

    @property
    def get_monitors(self) -> bool:
        return (
            self._details.setdefault(
                "get_monitors", DEFAULT["details"].get("get_monitors")
            )
            == "1"
        )

    @get_monitors.setter
    def get_monitors(self, value: bool):
        self._details["get_monitors"] = "1" if value else "0"

    @property
    def control_monitors(self) -> bool:
        return (
            self._details.setdefault(
                "control_monitors", DEFAULT["details"].get("control_monitors")
            )
            == "1"
        )

    @control_monitors.setter
    def control_monitors(self, value: bool):
        self._details["control_monitors"] = "1" if value else "0"

    @property
    def get_logs(self) -> bool:
        return (
            self._details.setdefault("get_logs", DEFAULT["details"].get("get_logs"))
            == "1"
        )

    @get_logs.setter
    def get_logs(self, value: bool):
        self._details["get_logs"] = "1" if value else "0"

    @property
    def watch_stream(self) -> bool:
        return (
            self._details.setdefault(
                "watch_stream", DEFAULT["details"].get("watch_stream")
            )
            == "1"
        )

    @watch_stream.setter
    def watch_stream(self, value: bool):
        self._details["watch_stream"] = "1" if value else "0"

    @property
    def watch_snapshot(self) -> bool:
        return (
            self._details.setdefault(
                "watch_snapshot", DEFAULT["details"].get("watch_snapshot")
            )
            == "1"
        )

    @watch_snapshot.setter
    def watch_snapshot(self, value: bool):
        self._details["watch_snapshot"] = "1" if value else "0"

    @property
    def watch_videos(self) -> bool:
        return (
            self._details.setdefault(
                "watch_videos", DEFAULT["details"].get("watch_videos")
            )
            == "1"
        )

    @watch_videos.setter
    def watch_videos(self, value: bool):
        self._details["watch_videos"] = "1" if value else "0"

    @property
    def delete_videos(self) -> bool:
        return (
            self._details.setdefault(
                "delete_videos", DEFAULT["details"].get("delete_videos")
            )
            == "1"
        )

    @delete_videos.setter
    def delete_videos(self, value: bool):
        self._details["delete_videos"] = "1" if value else "0"


class Key:
    def __init__(self, key: dict = None):
        if key is None:
            key = {}
        self._dict = key

    @property
    def code(self) -> Optional[str]:
        return self._dict.get("code")

    @property
    def ip(self) -> str:
        return self._dict.setdefault("ip", "0.0.0.0")

    @ip.setter
    def ip(self, value: str):
        self._dict["ip"] = "0.0.0.0" if value is None else value

    @property
    def details(self):
        return Details(self._dict.setdefault("details", {}))


async def async_add(connection: Connection, key: dict) -> Key:
    body = {
        "data": {
            "ip": key.get("ip", DEFAULT["ip"]),
            "details": {
                wk: key.get("details", {}).get(wk, DEFAULT["details"][wk])
                for wk in DEFAULT["details"].keys()
            },
        }
    }

    return Key(await connection.post(connection.action_url(ACTION, "add"), body, "api"))


class Manager:
    def __init__(self, connection: Connection):
        self._connection = connection

    async def all(self):
        """
        Get a list of API keys for the current connection
        """

        json = await self._connection.get(self._connection.action_url(ACTION, "list"))
        return list(map(Key, json["list"]))

    async def add(self, key: Union[Key, dict]):
        if isinstance(key, Key):
            key = key._dict

        return await async_add(self._connection, key)

    async def delete(self, key: Union[Key, dict]):
        if isinstance(key, Key):
            key = key._dict

        await self._connection.post(
            self._connection.action_url(ACTION, "delete"),
            body={"data": {"code": key.get("code")}},
        )
