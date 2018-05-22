from pyetcd.client import Client


def test_version():
    c = Client()
    assert c.version() == '3.2.18'
