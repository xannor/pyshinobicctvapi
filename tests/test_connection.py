from pyshinobicctvapi.connection import Connection


def test_create():
    assert not Connection("") is None