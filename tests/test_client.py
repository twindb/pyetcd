#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyetcd
----------------------------------

Tests for `pyetcd` module.
"""
import mock as mock

import pytest
from requests import ConnectionError
from pyetcd import EtcdException
from pyetcd.client import Client, ClientException


@pytest.fixture
def default_etcd():
    return Client()


def test_client_defaults(default_etcd):
    assert default_etcd._hosts[0][0] == '127.0.0.1'
    assert default_etcd._hosts[0][1] == 2379
    assert default_etcd._protocol == 'http'
    assert default_etcd._srv_domain is None
    assert default_etcd._version_prefix == 'v2'
    assert default_etcd._urls[0] == 'http://127.0.0.1:2379/v2/keys'


def test_client_hosts_str():
    client = Client(host='10.10.10.10', port=1111)
    assert client._hosts[0][0] == '10.10.10.10'
    assert client._hosts[0][1] == 1111
    assert client._urls[0] == 'http://10.10.10.10:1111/v2/keys'


def test_client_hosts_list():
    client = Client(host=['10.10.10.10',
                          '10.10.10.20'])
    assert client._hosts[0][0] == '10.10.10.10'
    assert client._hosts[0][1] == 2379
    assert client._hosts[1][0] == '10.10.10.20'
    assert client._hosts[1][1] == 2379
    assert client._urls == [
        'http://10.10.10.10:2379/v2/keys',
        'http://10.10.10.20:2379/v2/keys',
    ]


def test_client_hosts_tuples():
    client = Client(host=[('10.10.10.10', 1111),
                          ('10.10.10.20', 2222)])
    assert client._hosts[0][0] == "10.10.10.10"
    assert client._hosts[0][1] == 1111
    assert client._hosts[1][0] == "10.10.10.20"
    assert client._hosts[1][1] == 2222
    assert client._urls == [
        'http://10.10.10.10:1111/v2/keys',
        'http://10.10.10.20:2222/v2/keys',
    ]


def test_client_raises_exception_if_unsupported_protocol():
    Client(protocol='http')
    with pytest.raises(ClientException):
        Client(protocol='foo')


@mock.patch('pyetcd.client.requests')
def test_write(mock_requests, default_etcd):
    mock_payload = mock.Mock()
    mock_payload.content = """
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
    mock_requests.put.return_value = mock_payload
    response = default_etcd.write('/messsage', 'Hello world')
    assert response.action == 'set'
    assert response.node['value'] == 'Hello world'


@mock.patch('pyetcd.client.requests')
def test_write_raises_exception(mock_requests, default_etcd):
    mock_requests.put.side_effect = ConnectionError
    with pytest.raises(EtcdException):
        default_etcd.write('/messsage', 'Hello world')


@mock.patch('pyetcd.client.requests')
def test_read(mock_requests, default_etcd):
    mock_payload = mock.Mock()
    mock_payload.content = """
        {
            "action": "get",
            "node": {
                "createdIndex": 28,
                "key": "/messsage",
                "modifiedIndex": 28,
                "value": "Hello world"
            }
        }
    """
    mock_requests.get.return_value = mock_payload
    response = default_etcd.read('/messsage')
    assert response.action == 'get'
    assert response.node['value'] == 'Hello world'


@mock.patch('pyetcd.client.requests.get')
def test_read_wait(mock_get, default_etcd):
    mock_payload = mock.Mock()
    mock_payload.content = """
            {
                "action": "set",
                "node": {
                    "createdIndex": 30,
                    "key": "/messsage",
                    "modifiedIndex": 30,
                    "value": "foo"
                },
                "prevNode": {
                    "createdIndex": 29,
                    "key": "/messsage",
                    "modifiedIndex": 29,
                    "value": "bar"
                }
            }
        """
    mock_get.return_value = mock_payload
    response = default_etcd.read('/messsage', wait=True)
    assert response.action == 'set'
    assert response.node['value'] == 'foo'
    mock_get.assert_called_once_with(
        'http://127.0.0.1:2379/v2/keys/messsage?wait=true')


@mock.patch('pyetcd.client.requests')
def test_read_raises_exception(mock_requests, default_etcd):
    mock_requests.get.side_effect = ConnectionError
    with pytest.raises(EtcdException):
        default_etcd.read('/messsage')


@mock.patch('pyetcd.client.requests')
def test_read_exception_no_key(mock_requests, default_etcd):
    payload = '{"errorCode":100,"message":"Key not found",' \
              '"cause":"/foo","index":38}'
    mock_response = mock.MagicMock()
    mock_response.content = payload
    mock_requests.get.return_value = mock_response
    with pytest.raises(EtcdException):
        default_etcd.read('/foo')


@mock.patch('pyetcd.client.requests')
def test_read_exception_unknown_error(mock_requests, default_etcd):
    payload = '{"errorCode":1000,"message":"Unknown error",' \
              '"cause":"/foo","index":38}'
    mock_response = mock.MagicMock()
    mock_response.content = payload
    mock_requests.get.return_value = mock_response
    with pytest.raises(EtcdException):
        default_etcd.read('/foo')


@mock.patch('pyetcd.client.requests')
def test_delete(mock_requests, default_etcd):
    payload = """
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
    mock_response = mock.MagicMock()
    mock_response.content = payload
    mock_requests.delete.return_value = mock_response
    default_etcd.delete('/foo')
    mock_requests.delete.assert_called_once_with('http://127.0.0.1:2379/v2/keys/foo')


@mock.patch('pyetcd.client.requests')
def test_delete_exception(mock_requests, default_etcd):
    payload = """
    {"errorCode":100,"message":"Key not found","cause":"/foo","index":40}
    """
    mock_response = mock.MagicMock()
    mock_response.content = payload
    mock_requests.delete.return_value = mock_response
    with pytest.raises(EtcdException):
        default_etcd.delete('/foo')
