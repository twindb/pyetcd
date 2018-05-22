"""module to connect to an etcd node and perform low rest API requests."""
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
    Etcd Client class.

    :param kwargs: Keyword arguments:

        - **host** (str, list(str), list(tuple)) - etcd node hostname
            or list of hostnames
            or list of tuples (hostname, port).
            Default is '127.0.0.1'.
        - **port** (int) - TCP port to connect to. Default is 2379.
        - **srv_domain** (str) - Domain name if DNS discovery is used
        - **version_prefix** (str) - API version prefix. Default is 'v2'.
        - **allow_reconnect** (bool) - If client fails to connect to
            a cluster node connect to the next node in the cluster.
            Default is True.
        - **protocol** (str) - Protocol to connect to the cluster.
            Default is 'http'.
    :raise ClientException: if any errors
    :raise NotImplementedError: if there is an attempt to use unsupported
        DNS discovery.
    """
    def __init__(self, **kwargs):
        if 'srv_domain' in kwargs:
            raise NotImplementedError('DNS discovery is not implemented')

        self._allow_reconnect = kwargs.get('allow_reconnect', True)
        protocol = kwargs.get('protocol', 'http')
        if protocol in SUPPORTED_PROTOCOLS:
            self._protocol = protocol
        else:
            raise ClientException('Protocol %s is unsupported' % protocol)
        self._version_prefix = kwargs.get('version_prefix', 'v2')
        self._srv_domain = None
        self._hosts = []
        self._urls = []
        host = kwargs.get('host', '127.0.0.1')
        port = kwargs.get('port', 2379)
        if isinstance(host, list):
            for host_item in host:
                if isinstance(host_item, tuple):
                    self._hosts.append(host_item)
                    url = "{protocol}://{host}:{port}" \
                        .format(protocol=self._protocol,
                                host=host_item[0],
                                port=host_item[1])
                    self._urls.append(url)
                else:
                    self._hosts.append((host_item, port))
                    url = "{protocol}://{host}:{port}" \
                        .format(protocol=self._protocol,
                                host=host_item,
                                port=port)
                    self._urls.append(url)

        else:
            self._hosts.append((host, port))
            url = "{protocol}://{host}:{port}" \
                .format(protocol=self._protocol,
                        host=host,
                        port=port)
            self._urls.append(url)
        self._session = requests.Session()

    def write(self, key, value, ttl=None):
        """
        Write value to a key

        :param key: Key
        :param value: Value
        :param ttl: Keys in etcd can be set to expire after a specified number
            of seconds. You can do this by setting a TTL (time to live)
            on the key.
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        data = {
            'value': value
        }
        if ttl and ttl > 0:
            data['ttl'] = int(ttl)
        return self._request_key(key, method='put', data=data)

    def read(self, key, **kwargs):
        """
        Read key value

        :param key: Key
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        return self._request_key(key, params=kwargs)

    def delete(self, key):
        """
        Delete a key

        :param key: Key
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        return self._request_key(key, method='delete')

    def version(self):
        """
        Return Etcd server version

        :return: string with Etcd server version. E.g. '2.3.7'
        :rtype: str
        """
        response = self._request_call('/version')
        return response.version_etcdserver

    def version_server(self):
        """
        Same as .version()

        :return: string with Etcd server version. E.g. '2.3.7'
        :rtype: str
        """
        return self.version()

    def version_cluster(self):
        """
        Return Etcd cluster version

        :return: string with Etcd cluster version. E.g. '2.3.0'
        :rtype: str
        """
        response = self._request_call('/version')
        return response.version_etcdcluster

    @property
    def health(self):
        """
        :return: True if the node is healthy
        :rtype: bool
        """
        return self._request_call('/health').health

    def mkdir(self, directory):
        """
        Create directory

        :param directory: string with directory name
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """
        data = {
            'dir': True,
            'prevExist': False
        }
        return self._request_key(directory, method='put', data=data)

    def rmdir(self, directory, recursive=False):
        """
        Delete directory

        :param directory: string with directory name
        :param recursive: recursively delete directory if not empty
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error
        """

        params = {
            'dir': 'true'
        }
        if recursive:
            params['recursive'] = 'true'

        return self._request_key(directory, params=params, method='delete')

    def compare_and_swap(  # pylint: disable=too-many-arguments
            self,
            key, value,
            prev_value=None,
            prev_index=None,
            prev_exist=None,
            ttl=None):
        """
        This command will set the value of a key only if the client-provided
        conditions are equal to the current conditions.

        :param key: key string
        :param value: key value
        :param prev_value: checks the previous value of the key.
        :param prev_index: checks the previous modifiedIndex of the key.
        :param prev_exist: checks existence of the key: if prevExist is True,
            it is an update request; if prevExist is False,
            it is a create request.
        :param ttl: set ttl on the key in seconds
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error.
        :raise EtcdNodeExist: if condition ``prev_exist=False`` fails.
        :raise EtcdTestFailed: if condition ``prev_value='bar'`` fails.
        """
        data = {
            'value': value
        }
        if ttl:
            data['ttl'] = ttl

        params = None

        if prev_exist is not None:
            params = {
                'prevExist': prev_exist
            }

        if prev_value is not None:
            params = {
                'prevValue': prev_value
            }

        if prev_index is not None:
            params = {
                'prevIndex': prev_index
            }

        return self._request_key(key, method='put',
                                 params=params, data=data)

    def compare_and_delete(self, key, prev_value=None, prev_index=None):
        """
        This command will delete a key only if the client-provided
        conditions are equal to the current conditions.

        :param key: the key
        :param prev_value: checks the previous value of the key.
        :param prev_index: checks the previous modifiedIndex of the key.
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error.
        :raise EtcdNodeExist: if any condition fails.
        """
        params = None

        if prev_value is not None:
            params = {
                'prevValue': prev_value
            }

        if prev_index is not None:
            params = {
                'prevIndex': prev_index
            }

        return self._request_key(key, method='delete', params=params)

    def update_ttl(self, key, ttl):
        """
        Update key's ttl

        :param key: the key
        :param ttl: new ttl
        :return: Result of operation.
        :rtype: EtcdResult
        :raise EtcdException: if etcd responds with error or HTTP error.
        :raise EtcdKeyNotFound: if the key doesn't exist
        """
        data = {
            'ttl': ttl,
            'refresh': 'true',
            'prevExist': 'true'
        }

        return self._request_key(key, method='put', data=data)

    def _request_key(self, key, method='get', params=None, **kwargs):
        """
        Make an API call on a key

        :param key: key string. must start with '/'
        :param method: HTTP method in lower case (put, get, post, etc)
        :param params: dictionary with parameters that will be added to URI
        :type params: dict
        :param kwargs: keyword arguments to be passed down to _request_call()
        :return: Result of operation.
        :rtype: EtcdResult
        """
        uri = "/{version_prefix}/keys{key}".format(
            version_prefix=self._version_prefix,
            key=key
        )
        if params:
            uri += "?"
            sep = ""
            for param, value in sorted(params.items()):
                if isinstance(value, bool):
                    value = str(value).lower()
                uri += "%s%s=%s" % (sep, param, value)
                sep = "&"
        return self._request_call(uri, method=method, **kwargs)

    def _request_call(self, uri, method='get', **kwargs):
        if self._allow_reconnect:
            urls = self._urls
        else:
            urls = [self._urls[0]]
        error_messages = []
        for endpoint in urls:
            try:
                url = endpoint + uri

                return EtcdResult(
                    getattr(self._session, method)(
                        url,
                        **kwargs
                    )
                )
            except RequestException as err:
                error_messages.append("%s: %s" % (endpoint, err))

        raise EtcdException(
            'No more hosts to connect.\nErrors: %s'
            % '\n'.join(error_messages)
        )
