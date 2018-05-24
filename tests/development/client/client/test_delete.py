from pyetcd.client import Client


def test_delete():
    c = Client(allow_reconnect=False)
    # c.remove_member('af48860468db8641')
    c.remove_member('e907142111645c1c')
    # assert c.health is True
