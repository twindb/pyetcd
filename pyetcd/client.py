# -*- coding: utf-8 -*-
import requests
from requests import ConnectionError

from pyetcd import EtcdResult, EtcdException

SUPPORTED_PROTOCOLS = ['http']


class ClientException(Exception):
    """
    Exception for errors in Client class
    """


class Client(object):
    """
    Etcd Client class
    """
    def __init__(self,
                 host='127.0.0.1',
                 port=2379,
                 srv_domain=None,
                 version_prefix='v2',
                 protocol='http'):
        """
        Initialize Client class instance

        :param host: hostname or list of hostnames
        or list of tuples (hostname, port)
        :param port: TCP port to connect to (default=2379)
        :param srv_domain: Domain name if DNS discovery is used
        :param version_prefix: API version prefix (default='v2')
        :param protocol: Protocol to connect to the cluster (default='http')
        :raise ClientException: if any errors
        """
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
        of seconds. You can do this by setting a TTL (time to live) on the key.
        :return: EtcdResult
        :raise: EtcdException
        """
        data = {
            'value': value
        }
        try:
            response = requests.put(self._urls[0] + key, data=data)
            return EtcdResult(response)
        except ConnectionError as err:
            raise EtcdException(err)

    def read(self, key, wait=False):
        """
        Read key value

        :param key: Key
        :param wait: Wait until the key value changes (default=False)
        :return: EtcdResult
        :raise: EtcdException
        """
        try:
            url = self._urls[0] + key

            if wait:
                url += "?wait=true"

            return EtcdResult(requests.get(url))
        except ConnectionError as err:
            raise EtcdException(err)

    def delete(self, key):
        """
        Delete a key

        :param key: Key
        :return: EtcdResult
        :raise: EtcdException
        """
        try:
            url = self._urls[0] + key
            return EtcdResult(requests.delete(url))
        except ConnectionError as err:
            raise EtcdException(err)
