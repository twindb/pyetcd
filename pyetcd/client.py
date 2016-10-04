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
                    url = "{protocol}://{host}:{port}" \
                        .format(protocol=self._protocol,
                                host=h[0],
                                port=h[1])
                    self._urls.append(url)
                else:
                    self._hosts.append((h, port))
                    url = "{protocol}://{host}:{port}" \
                        .format(protocol=self._protocol,
                                host=h,
                                port=port)
                    self._urls.append(url)

        else:
            self._hosts.append((host, port))
            url = "{protocol}://{host}:{port}" \
                .format(protocol=self._protocol,
                        host=host,
                        port=port)
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
        return self._request_key(key, method='put', data=data)

    def read(self, key, wait=False):
        """
        Read key value

        :param key: Key
        :param wait: Wait until the key value changes (default=False)
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        return self._request_key(key, wait=wait)

    def delete(self, key):
        """
        Delete a key

        :param key: Key
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        return self._request_key(key, method='delete')

    def version(self):
        """
        Return Etcd server version

        :return: string with Etcd server version. E.g. '2.3.7'
        """
        response = self._request_call('/version')
        return response.version_etcdserver

    def version_server(self):
        """
        Same as .version()

        :return: string with Etcd server version. E.g. '2.3.7'
        """
        return self.version()

    def version_cluster(self):
        """
        Return Etcd cluster version

        :return: string with Etcd cluster version. E.g. '2.3.0'
        """
        response = self._request_call('/version')
        return response.version_etcdcluster

    def mkdir(self, directory):
        """
        Create directory

        :param directory: string with directory name
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        data = {
            'dir': True
        }
        return self._request_key(directory, method='put', data=data)

    def rmdir(self, directory, recursive=False):
        """
        Delete directory

        :param directory: string with directory name
        :return: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        data = {
            'dir': True
        }
        if recursive:
            data['recursive'] = True
        return self._request_key(directory, method='delete', data=data)

    def _request_key(self, key, **kwargs):
        uri = "/{version_prefix}/keys{key}".format(
            version_prefix=self._version_prefix,
            key=key
        )
        return self._request_call(uri, **kwargs)

    def _request_call(self, uri, method='get', wait=False, **kwargs):
        print(uri)
        if self._allow_reconnect:
            urls = self._urls
        else:
            urls = [self._urls[0]]
        for u in urls:
            try:
                url = u + uri

                if wait:
                    url += "?wait=true"

                return EtcdResult(getattr(requests, method)(url, **kwargs))
            except RequestException:
                pass
        raise EtcdException('No more hosts to connect')
