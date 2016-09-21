# -*- coding: utf-8 -*-
import requests
from requests import RequestException

from pyetcd import EtcdResult, EtcdException

SUPPORTED_PROTOCOLS = ['http']


class ClientException(Exception):
    """
    Exception for errors in Client class
    """


class Client(object):
    """
    Etcd Client class

    :param host: etcd node hostname or list of hostnames
        or list of tuples (hostname, port) (default='127.0.0.1')
    :param port: TCP port to connect to (default=2379)
    :param srv_domain: Domain name if DNS discovery is used
    :param version_prefix: API version prefix (default='v2')
    :param allow_reconnect: If client fails to connect to a cluster node
        connect to the next node in the cluster
    :param protocol: Protocol to connect to the cluster (default='http')
    :raise ClientException: if any errors
    """
    def __init__(self,
                 host='127.0.0.1',
                 port=2379,
                 srv_domain=None,
                 version_prefix='v2',
                 protocol='http',
                 allow_reconnect=True):
        # TODO: implement DNS discovery
        if srv_domain:
            raise ClientException('Not implemented')

        self._allow_reconnect = allow_reconnect
        if protocol in SUPPORTED_PROTOCOLS:
            self._protocol = protocol
        else:
            raise ClientException('Protocol %s is unsupported' % protocol)
        self._version_prefix = version_prefix
        self._srv_domain = srv_domain
        self._hosts = []
        self._urls = []
        if isinstance(host, list):
            for h in host:
                if isinstance(h, tuple):
                    self._hosts.append(h)
                    url = "{protocol}://{host}:{port}/" \
                          "{version_prefix}/keys" \
                        .format(protocol=self._protocol,
                                host=h[0],
                                port=h[1],
                                version_prefix=self._version_prefix)
                    self._urls.append(url)
                else:
                    self._hosts.append((h, port))
                    url = "{protocol}://{host}:{port}/" \
                          "{version_prefix}/keys" \
                        .format(protocol=self._protocol,
                                host=h,
                                port=port,
                                version_prefix=self._version_prefix)
                    self._urls.append(url)

        else:
            self._hosts.append((host, port))
            url = "{protocol}://{host}:{port}/{version_prefix}/keys" \
                .format(protocol=self._protocol,
                        host=host,
                        port=port,
                        version_prefix=self._version_prefix)
            self._urls.append(url)

    def write(self, key, value, ttl=None):
        """
        Write value to a key

        :param key: Key
        :param value: Value
        :param ttl: Keys in etcd can be set to expire after a specified number
            of seconds. You can do this by setting a TTL (time to live)
            on the key.
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        # TODO implement ttl
        if ttl:
            raise EtcdException('Not implemented')

        data = {
            'value': value
        }
        return self._request_call(key, method='put', data=data)

    def read(self, key, wait=False):
        """
        Read key value

        :param key: Key
        :param wait: Wait until the key value changes (default=False)
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        return self._request_call(key, wait=wait)

    def delete(self, key):
        """
        Delete a key

        :param key: Key
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        return self._request_call(key, method='delete')

    def _request_call(self, key, method='get', wait=False, **kwargs):
        if self._allow_reconnect:
            urls = self._urls
        else:
            urls = [self._urls[0]]
        for u in urls:
            try:
                url = u + key

                if wait:
                    url += "?wait=true"

                return EtcdResult(getattr(requests, method)(url, **kwargs))
            except RequestException:
                pass
        raise EtcdException('No more hosts to connect')
