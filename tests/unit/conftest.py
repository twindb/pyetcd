import pytest

from pyetcd.client import Client


@pytest.fixture
def default_etcd():
    return Client()


@pytest.fixture
def payload_read_success():
    return """
        {
            "action": "get",
            "node": {
                "createdIndex": 28,
                "key": "/foo",
                "modifiedIndex": 28,
                "value": "Hello world"
            }
        }
    """


@pytest.fixture
def payload_write_success():
    return """
        {
            "action": "set",
            "node": {
                "createdIndex": 28,
                "key": "/messsage",
                "modifiedIndex": 28,
                "value": "Hello world"
            },
            "prevNode": {
                "createdIndex": 27,
                "key": "/messsage",
                "modifiedIndex": 27,
                "value": "Hello world"
            }
        }
    """


@pytest.fixture
def payload_write_ttl_success():
    return """
        {
            "action": "set",
            "node": {
                "createdIndex": 5,
                "expiration": "2013-12-04T12:01:21.874888581-08:00",
                "key": "/foo",
                "modifiedIndex": 5,
                "ttl": 5,
                "value": "bar"
            }
        }
    """


@pytest.fixture
def payload_delete_success():
    return """
        {
            "action": "delete",
            "node": {
                "createdIndex": 39,
                "key": "/foo",
                "modifiedIndex": 40
            },
            "prevNode": {
                "createdIndex": 39,
                "key": "/foo",
                "modifiedIndex": 39,
                "value": "aaa"
            }
        }
    """


@pytest.fixture
def payload_self():
    return """
{
    "id": "ce2a822cea30bfca",
    "leaderInfo": {
        "leader": "ce2a822cea30bfca",
        "startTime": "2016-09-19T06:08:51.937661067Z",
        "uptime": "17h5m58.934381551s"
    },
    "name": "default",
    "recvAppendRequestCnt": 0,
    "sendAppendRequestCnt": 0,
    "startTime": "2016-09-19T06:08:51.527241706Z",
    "state": "StateLeader"
}"""
