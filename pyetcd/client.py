# -*- coding: utf-8 -*-

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
            self.protocol = protocol
        else:
            raise ClientException('Protocol %s is unsupported' % protocol)
        self.version_prefix = version_prefix
        self.srv_domain = srv_domain
        self.port = port
        self.host = host

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

    def read(self, key, wait=False):
        """
        Read key value

        :param key: Key
        :param wait: Wait until the key value changes (default=False)
        :return: EtcdResult
        :raise: EtcdException
        """

    def delete(self, key):
        """
        Delete a key

        :param key: Key
        :return: EtcdResult
        :raise: EtcdException
        """
