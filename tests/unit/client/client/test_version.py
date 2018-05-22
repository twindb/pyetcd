import mock


def test_client_version_parse_response(default_etcd):
    payload = '{"etcdserver":"2.3.7","etcdcluster":"2.3.0"}'
    mock_response = mock.Mock(content=payload)
    mock_requests = mock.Mock()
    mock_requests.get = mock.Mock(side_effect=[mock_response])
    default_etcd._session = mock_requests
    assert default_etcd.version() == "2.3.7"


def test_client_version_no_index(default_etcd):
    payload = '{"etcdserver":"2.3.7","etcdcluster":"2.3.0"}'
    mock_response = mock.Mock(content=payload)

    def mock_getitem(inst, key):
        raise KeyError('x-etcd-index')

    mock_response.headers.__getitem__ = mock_getitem

    mock_requests = mock.Mock()
    mock_requests.get = mock.Mock(side_effect=[mock_response])
    default_etcd._session = mock_requests
    assert default_etcd.version() == "2.3.7"
