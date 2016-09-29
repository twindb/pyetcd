import shlex
import pytest
from subprocess import call
from pyetcd import EtcdNodeExist

__author__ = 'aleks'
from pyetcd.client import Client


@pytest.fixture
def client():
    # Clean database
    cmd = """
        for d in $(etcdctl ls)
        do
            etcdctl rm --recursive $d
        done
        """
    call(['bash', '-c', cmd])
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

    # print(response.node)
    #__author__ = 'aleks'
