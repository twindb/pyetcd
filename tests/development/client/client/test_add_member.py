from pyetcd.client import Client


def test_add():
    c = Client(allow_reconnect=False)
    r = c.add_member(['http://10.0.3.12:2380'])
    print(r)
    # assert c.health is True
