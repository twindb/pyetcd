import shlex

import json
import pytest
from subprocess import call

import requests

from pyetcd import EtcdNodeExist, EtcdDirNotEmpty
from pyetcd.client import Client


@pytest.fixture
def client():
    # Clean database
    http_response = requests.get('http://10.0.3.11:2379/v2/keys/')
    content = http_response.content
    node = json.loads(content)['node']
    try:
        for n in node['nodes']:
            key = n['key']
            requests.delete('http://10.0.3.10:2379/v2/keys{key}?recursive=true'.format(key=key))
    except KeyError:
        pass

    return Client([
        '10.0.3.10',
        '10.0.3.11',
        '10.0.3.12'
    ])


def test_mkdir(client):
    response = client.mkdir('/aaa')
    assert response.node['key'] == '/aaa'
    with pytest.raises(EtcdNodeExist):
        client.mkdir('/aaa')


def test_rmdir(client):
    response = client.mkdir('/aaa')
    assert response.node['key'] == '/aaa'
    response = client.rmdir('/aaa')
    assert response.node['key'] == '/aaa'


def test_rmdir_recursive(client):
    response = client.mkdir('/aaa/bbb')
    assert response.node['key'] == '/aaa/bbb'
    with pytest.raises(EtcdDirNotEmpty):
        client.rmdir('/aaa')
    client.rmdir('/aaa', recursive=True)
    assert response.node['key'] == '/aaa/bbb'
