from typing import Optional

from connection import Connection

class User:
    """
    Shinobi User API
    """

    def __init__(self, user: dict = None):
        if user is None:
            user = {}
        self._user = user

        #self._id = user['uid']

    @property
    def email(self) -> Optional[str]:
        return self._user.get('mail')

    @property
    def group(self) -> Optional[str]:
        return self._user.get('ke')