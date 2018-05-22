from pyetcd.client import Client


def test_version():
    c = Client()
    assert c.health is True
