import six
import hmac
import arrow
import hashlib
import datetime
import collections
from .query_encoder import QueryEncoder


def merge_two_dicts(d1, d2):
    d3 = d1.copy()
    d3.update(d2)
    return d3


class ArgumentError(Exception):
    pass


class Token(object):

    key = None
    secret = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def sign(self, request):
        request.sign(self)


class Request(object):

    path = None
    method = None
    signed = False
    auth_dict = None
    query_dict = None

    AUTH_VERSION = '1.0'

    ISO8601 = arrow.utcnow().format('YYYY-MM-DDTHH:mm:ssZZ')

    def __init__(self, method, path, query):
        if not isinstance(path, str):
            raise ArgumentError('Expected string')
        if not isinstance(query, dict):
            raise ArgumentError('Expected dict')

        query_dict = {}
        auth_dict = {}

        for key, value in query.items():
            key = key.lower()
            if 'auth_' in key:
                auth_dict[key] = value
            else:
                query_dict[key] = value

        self.method = method.upper()
        self.path = path
        self.query_dict = query_dict
        self.auth_dict = auth_dict
        self.signed = False

    # Sign the request with the given token, and return the computed
    # authentication parameters
    def sign(self, token, auth_timestamp=None):
        self.signed = True
        self.auth_dict = dict(
            auth_key=token.key,
            auth_version=self.AUTH_VERSION,
            auth_timestamp=auth_timestamp or arrow.utcnow().timestamp
        )
        self.auth_dict['auth_signature'] = self.signature(token)
        return self.auth_dict

    def parameter_string(self):
        param_hash = merge_two_dicts(self.query_dict, (self.auth_dict or {}))
        # Convert keys to lowercase strings
        params_dict = {}
        for key, value in param_hash.items():
            params_dict[key.lower()] = value

        # Exclude signature from signature generation!
        if 'auth_signature' in params_dict:
            del params_dict['auth_signature']

        params_dict = collections.OrderedDict(sorted(params_dict.items()))
        params_list = []
        for key, value in params_dict.items():
            params_list.append(QueryEncoder.encode_param_without_escaping(key, value))
        return '&'.join(params_list)

    def string_to_sign(self):
        return "\n".join([self.method, self.path, self.parameter_string()])

    def signature(self, token):
        msg = self.string_to_sign()
        if six.PY2: 
            return hmac.new(str(token.secret), msg, hashlib.sha256).hexdigest()
        else:
            return hmac.new(bytes(token.secret, 'utf8'), bytes(msg, 'utf8'), hashlib.sha256).hexdigest()
