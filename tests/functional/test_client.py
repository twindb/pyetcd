import json
from pprint import pprint
import pytest

import requests
import time

from pyetcd import EtcdNodeExist, EtcdDirNotEmpty, EtcdKeyNotFound, \
    EtcdTestFailed
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


@pytest.mark.parametrize('ttl', [
    1, 2
])
def test_write_ttl(ttl, client):
    response = client.write('/foo', 'bar', ttl=ttl)
    assert response.node['ttl'] == ttl
    time.sleep(ttl + 1)
    with pytest.raises(EtcdKeyNotFound):
        client.read('/foo')


def test_client_cas_prev_exist(client):
    client.compare_and_swap('/foo', 'bar1')
    with pytest.raises(EtcdNodeExist):
        client.compare_and_swap('/foo', 'bar2', prev_exist=False)


def test_client_cas_prev_value(client):
    client.compare_and_swap('/foo', 'bar')
    with pytest.raises(EtcdTestFailed):
        client.compare_and_swap('/foo', 'bar2', prev_value='bar1')


def test_client_cas_prev_index(client):
    response = client.compare_and_swap('/foo', 'bar')
    modifiedIndex = response.node['modifiedIndex']
    client.compare_and_swap('/foo', 'bar2', prev_index=modifiedIndex)
    with pytest.raises(EtcdTestFailed):
        client.compare_and_swap('/foo', 'bar2', prev_index=modifiedIndex)


def test_client_cad_prev_value(client):
    client.write('/foo', 'bar')
    client.compare_and_delete('/foo', prev_value='bar')

    client.write('/foo', 'bar')
    with pytest.raises(EtcdTestFailed):
        client.compare_and_delete('/foo', prev_value='bar1')


def test_client_cad_prev_index(client):
    response = client.write('/foo', 'bar')
    modifiedIndex = response.node['modifiedIndex']
    client.compare_and_delete('/foo', prev_index=modifiedIndex)

    client.write('/foo', 'bar')
    with pytest.raises(EtcdTestFailed):
        client.compare_and_delete('/foo', prev_index=modifiedIndex)


def test_client_cas_prev_exist_ttl(client):
    client.compare_and_swap('/foo', 'bar', ttl=100)
    with pytest.raises(EtcdNodeExist):
        client.compare_and_swap('/foo', 'bar2', prev_exist=False)


def test_client_update_ttl(client):
    client.write('/foo', 'bar', ttl=100)
    r = client.update_ttl('/foo', 1000)
    assert r.node['ttl'] == 1000
