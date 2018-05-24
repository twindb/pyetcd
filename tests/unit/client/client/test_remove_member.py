import mock

from pyetcd.client import Client


@mock.patch.object(Client, '_request_call')
def test_remove_member(mock_call, default_etcd):
    default_etcd.remove_member('foo')
    mock_call.assert_called_once_with(
        '/v2/members/foo',
        method='delete'
    )
