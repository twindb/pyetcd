import mock
import pytest


@pytest.mark.parametrize('payload, health', [
    (
        '{"health":"true"}',
        True
    ),
    (
        '{"health":"false"}',
        False
    )
])
def test_health(default_etcd, payload, health):
    mock_response = mock.Mock(content=payload)
    mock_requests = mock.Mock()
    mock_requests.get = mock.Mock(side_effect=[mock_response])
    default_etcd._session = mock_requests
    assert default_etcd.health is health
