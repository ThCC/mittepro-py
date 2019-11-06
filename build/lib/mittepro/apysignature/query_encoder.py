import six
import json
import urllib


class QueryEncoder(object):

    @staticmethod
    def encode_param(key, value):
        if isinstance(value, list):
            return '&'.join([QueryEncoder.escape(key) + '[]=' + QueryEncoder.escape(item) for item in value])
        else:
            return QueryEncoder.escape(key) + '=' + QueryEncoder.escape(value)

    @staticmethod
    def encode_param_without_escaping(key, value):
        if isinstance(value, list):
            return str('&'.join([key + '[]=' + item for item in value]))
        else:
            if isinstance(value, dict):
                value = json.dumps(value)
            elif six.PY2 and isinstance(value, unicode):
                value = str(value.encode('utf-8'))
        return "{key}={value}".format(key=key, value=value)

    @staticmethod
    def escape(s):
        if six.PY2:
            return urllib.quote(s, '')
        else:
            return urllib.parse.quote(s, '')
