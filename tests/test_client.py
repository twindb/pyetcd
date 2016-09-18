#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyetcd
----------------------------------

Tests for `pyetcd` module.
"""

import pytest
from pyetcd.client import Client, ClientException


def test_client_defaults():
    client = Client()
    assert client.host == '127.0.0.1'
    assert client.port == 2379
    assert client.protocol == 'http'
    assert client.srv_domain is None
    assert client.version_prefix == 'v2'


def test_client_raises_exception_if_unsupported_protocol():
    Client(protocol='http')
    with pytest.raises(ClientException):
        Client(protocol='foo')
