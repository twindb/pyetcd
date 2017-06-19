# -*- coding: utf-8 -*-
import json

__author__ = 'TwinDB Development Team'
__email__ = 'dev@twindb.com'
__version__ = '1.7.0'


# Exceptions

class EtcdException(Exception):
    """
    Generic Etcd error.
    """


class EtcdKeyNotFound(EtcdException):
    """
    Error EcodeKeyNotFound (http code 100)
    """


class EtcdTestFailed(EtcdException):
    """
    Error EcodeTestFailed (http code 101)
    """


class EtcdNotFile(EtcdException):
    """
    Error EcodeNotFile (http code 102)
    """


class EtcdNoMorePeer(EtcdException):
    """
    Error ecodeNoMorePeer (http code 103)
    """


class EtcdNotDir(EtcdException):
    """
    Error EcodeNotDir (http code 104)
    """


class EtcdNodeExist(EtcdException):
    """
    Error EcodeNodeExist (http code 105)
    """


class EtcdKeyIsPreserved(EtcdException):
    """
    Error ecodeKeyIsPreserved (http code 106)
    """


class EtcdRootROnly(EtcdException):
    """
    Error EcodeRootROnly (http code 107)
    """


class EtcdDirNotEmpty(EtcdException):
    """
    Error EcodeDirNotEmpty (http code 108)
    """


class EtcdExistingPeerAddr(EtcdException):
    """
    Error ecodeExistingPeerAddr (http code 109)
    """


class EtcdUnauthorized(EtcdException):
    """
    Error EcodeUnauthorized (http code 110)
    """


class EtcdValueRequired(EtcdException):
    """
    Error ecodeValueRequired (http code 200)
    """


class EtcdPrevValueRequired(EtcdException):
    """
    Error EcodePrevValueRequired (http code 201)
    """


class EtcdTTLNaN(EtcdException):
    """
    Error EcodeTTLNaN (http code 202)
    """


class EtcdIndexNaN(EtcdException):
    """
    Error EcodeIndexNaN (http code 203)
    """


class EtcdValueOrTTLRequired(EtcdException):
    """
    Error ecodeValueOrTTLRequired (http code 204)
    """


class EtcdTimeoutNaN(EtcdException):
    """
    Error ecodeTimeoutNaN (http code 205)
    """


class EtcdNameRequired(EtcdException):
    """
    Error ecodeNameRequired (http code 206)
    """


class EtcdIndexOrValueRequired(EtcdException):
    """
    Error ecodeIndexOrValueRequired (http code 207)
    """


class EtcdIndexValueMutex(EtcdException):
    """
    Error ecodeIndexValueMutex (http code 208)
    """


class EtcdInvalidField(EtcdException):
    """
    Error EcodeInvalidField (http code 209)
    """


class EtcdInvalidForm(EtcdException):
    """
    Error EcodeInvalidForm (http code 210)
    """


class EtcdRefreshValue(EtcdException):
    """
    Error EcodeRefreshValue (http code 211)
    """


class EtcdRefreshTTLRequired(EtcdException):
    """
    Error EcodeRefreshTTLRequired (http code 212)
    """


class EtcdRaftInternal(EtcdException):
    """
    Error EcodeRaftInternal (http code 300)
    """


class EtcdLeaderElect(EtcdException):
    """
    Error EcodeLeaderElect (http code 301)
    """


class EtcdWatcherCleared(EtcdException):
    """
    Error EcodeWatcherCleared (http code 400)
    """


class EtcdEventIndexCleared(EtcdException):
    """
    Error EcodeEventIndexCleared (http code 401)
    """


class EtcdStandbyInternal(EtcdException):
    """
    Error ecodeStandbyInternal (http code 402)
    """


class EtcdInvalidActiveSize(EtcdException):
    """
    Error ecodeInvalidActiveSize (http code 403)
    """


class EtcdInvalidRemoveDelay(EtcdException):
    """
    Error ecodeInvalidRemoveDelay (http code 404)
    """


class EtcdClientInternal(EtcdException):
    """
    Error ecodeClientInternal (http code 500)
    """


class EtcdResult(object):
    """
    Response from Etcd API

    :param response: Response from server as ``requests.(get|post|put)``
        returns.
    :raise EtcdException: if payload is invalid or contains errorCode.
    """
    _payload = None
    _exception_codes = {
        100: EtcdKeyNotFound,
        101: EtcdTestFailed,
        102: EtcdNotFile,
        103: EtcdNoMorePeer,
        104: EtcdNotDir,
        105: EtcdNodeExist,
        106: EtcdKeyIsPreserved,
        107: EtcdRootROnly,
        108: EtcdDirNotEmpty,
        109: EtcdExistingPeerAddr,
        110: EtcdUnauthorized,
        200: EtcdValueRequired,
        201: EtcdPrevValueRequired,
        202: EtcdTTLNaN,
        203: EtcdIndexNaN,
        204: EtcdValueOrTTLRequired,
        205: EtcdTimeoutNaN,
        206: EtcdNameRequired,
        207: EtcdIndexOrValueRequired,
        208: EtcdIndexValueMutex,
        209: EtcdInvalidField,
        210: EtcdInvalidForm,
        211: EtcdRefreshValue,
        212: EtcdRefreshTTLRequired,
        300: EtcdRaftInternal,
        301: EtcdLeaderElect,
        400: EtcdWatcherCleared,
        401: EtcdEventIndexCleared,
        402: EtcdStandbyInternal,
        403: EtcdInvalidActiveSize,
        404: EtcdInvalidRemoveDelay,
        500: EtcdClientInternal
    }

    def __init__(self, response):
        """
        Initialise EtcdResult instance
        """
        try:
            self._x_etcd_index = response.headers['X-Etcd-Index']
        except (TypeError, AttributeError):
            pass
        try:
            self._response_content = response.content
            self._payload = json.loads(response.content)
            self._raise_for_status(self._payload)
        except (ValueError, TypeError, AttributeError) as err:
            raise EtcdException(err)

    def __repr__(self):
        return self._response_content

    def _get_property(self, key):
        try:
            return self._payload[key]
        except KeyError:
            return None

    def _raise_for_status(self, payload):
        """
        Raise Etcd exception if payload contains errorCode
        :param payload: object decoded from JSON
        :raise EtcdException: if errorCode is present in payload
        """
        try:
            error_code = payload['errorCode']
            message = payload['message']
        except KeyError:
            return
        try:
            raise self._exception_codes[error_code](message)
        except KeyError:
            raise EtcdException(message)

    @property
    def x_etcd_index(self):
        try:
            return self._x_etcd_index
        except AttributeError:
            return None

    @property
    def action(self):
        """Action type"""
        return self._get_property('action')

    @property
    def node(self):
        """Node class instance. It holds the current key value."""
        return self._get_property('node')

    @property
    def prevNode(self):
        """Node class instance. It holds the previous key value."""
        return self._get_property('prevNode')

    @property
    def version_etcdcluster(self):
        """Version of Etcd cluster"""
        return self._get_property('etcdcluster')

    @property
    def version_etcdserver(self):
        """Version of Etcd server"""
        return self._get_property('etcdserver')

    @property
    def leader(self):
        """Leader of cluster"""
        return self._get_property('leader')

    @property
    def followers(self):
        """Followers of leader"""
        return self._get_property('followers')

    @property
    def id(self):
        """id"""
        return self._get_property('id')

    @property
    def leaderInfo(self):
        """leaderInfo"""
        return self._get_property('leaderInfo')

    @property
    def name(self):
        """name"""
        return self._get_property('name')

    @property
    def recvAppendRequestCnt(self):
        """recvAppendRequestCnt"""
        return self._get_property('recvAppendRequestCnt')

    @property
    def sendAppendRequestCnt(self):
        """sendAppendRequestCnt"""
        return self._get_property('sendAppendRequestCnt')

    @property
    def startTime(self):
        """startTime"""
        return self._get_property('startTime')

    @property
    def state(self):
        """state"""
        return self._get_property('state')


class ResponseNode(object):
    """
    Etcd response includes information about nodes.

    :param key: the HTTP path to which the request was made.
        We set /message to Hello world, so the key field is /message.
        etcd uses a file-system-like structure to represent
        the key-value pairs, therefore all keys start with /.
    :param value: the value of the key after resolving the request.
    :param created_index: an index is a unique, monotonically-incrementing
        integer created for each change to etcd. This specific index reflects
        the point in the etcd state member at which a given key was created
    :param modified_index: like node.createdIndex, this attribute is also
        an etcd index. Actions that cause the value to change include set,
        delete, update, create, compareAndSwap and compareAndDelete.
        Since the get and watch commands do not change state in the store,
        they do not change the value of node.modifiedIndex.
    """
    def __init__(self, key=None, value=None,
                 created_index=None,
                 modified_index=None):
        """
        Initialise ResponseNode instance
        """
        self.modifiedIndex = modified_index
        self.createdIndex = created_index
        self.value = value
        self.key = key
