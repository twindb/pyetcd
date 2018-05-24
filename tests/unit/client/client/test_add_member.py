import mock

from pyetcd.client import Client


@mock.patch.object(Client, '_request_call')
def test_add_member(mock_call, default_etcd):
    default_etcd.add_member(['foo'])
    mock_call.assert_called_once_with(
        '/v2/members',
        method='post',
        json={
            'peerURLs': ['foo']
        }
    )
