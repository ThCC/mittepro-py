import json
import logging
import requests
from mittepro.exceptions import APIError, TimeoutError
from apysignature.query_encoder import QueryEncoder
from apysignature.signature import Request as Request_sig, Token
from requests import Request, Session, ReadTimeout, ConnectTimeout, HTTPError

__author__ = 'thiagocdecastro'
__version__ = '1.8.6'
logging.basicConfig(format='%(asctime)s %(message)s')


def is_json(value):
    try:
        parsed = json.loads(value)
        return True
    except Exception:
        return False


def item_in_dict(dictionary, item):
    return item in dictionary and dictionary[item]


def item_not_in_dict(dictionary, item):
    return item not in dictionary or not dictionary[item]


def attr_in_instance(instance, attr):
    return hasattr(instance, attr) and getattr(instance, attr)


def attr_not_in_instance(instance, attr):
    return not hasattr(instance, attr) or not getattr(instance, attr)


def endpoint(method, endpoint):
    def decorator(func):
        def wrapped(self, *args, **kwargs):
            self.http_method = method
            self.endpoint = endpoint
            return func(self, *args, **kwargs)
        return wrapped
    return decorator


class Api(object):

    POST = 'POST'
    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'

    server_uri = ''
    urls = {}
    headers = {}
    endpoint = ''
    http_method = ''

    _api_key = ''
    _api_secret = ''

    def __init__(self, fail_silently=False, timeout_read=15):
        self._session = Session()
        self.timeout_read = timeout_read
        self.fail_silently = fail_silently

    def set_header(self, header):
        """
        :type header: dict
        :return:
        """
        self.headers.update(header)

    def get_headers(self):
        return self.headers

    def query_encode(self, url, payload):
        if '?' not in url:
            url += '?'
        else:
            url += '&'
        for key, value in payload.iteritems():
            url += QueryEncoder.encode_param(key, str(value)) + '&'
        return url.rstrip('&')

    def sign_request(self, payload=None):
        if not payload:
            payload = {}
        request = Request_sig(self.http_method, self.endpoint, payload)
        token = Token(self._api_key, self._api_secret)
        auth = request.sign(token)
        return auth

    def request(self, method=None, url=None, headers=None, payload=None, timeout_connect=10):
        if not url:
            url = self.endpoint
        if not method:
            method = self.http_method
        if not headers:
            headers = self.headers
        timeout = (timeout_connect, self.timeout_read)

        url = self.server_uri + url

        # Generate and sign request URL
        auth = self.sign_request()
        if auth:
            url = self.query_encode(url, auth)

        logging.info('EXTERNAL API: sending request on {0}'.format(url))
        try:
            if payload and method == 'GET':
                response = requests.get(url, payload)
            else:
                request = Request(
                    method, url,
                    json=payload,
                    headers=headers
                )
                prepped = request.prepare()
                response = self._session.send(prepped, timeout=timeout)

            valid_codes = (200, 201)
            if hasattr(response, 'status'):
                status_code = response.status
            else:
                status_code = response.status_code

            if response and status_code in valid_codes and response.content:
                response = json.loads(response.content)
            elif status_code not in valid_codes:
                logging.info("EXTERNAL API: request error: {0}".format(response.reason))
                if is_json(response.content):
                    content = json.loads(response.content)
                    msg = content['error'] if 'error' in content else content['detail']
                else:
                    msg = response.content[0:response.content.index('Request Method')].strip()
                if not self.fail_silently:
                    raise APIError(message_values=(msg.encode('utf8'),))
                response = {'error': msg.encode('utf8')}
            return response
        except ReadTimeout as e:
            logging.info("EXTERNAL API: request error: {0}".format(e))
            if not self.fail_silently:
                raise TimeoutError(message_values=(str(self.timeout_read),))
            else:
                return {'error': "The server did not respond within the time you stipulated. "
                                 "The time was {0} second(s)".format(str(self.timeout_read))}
        except (ConnectTimeout, HTTPError) as e:
            logging.info("EXTERNAL API: request error: {0}".format(e))
            if not self.fail_silently:
                raise e
            else:
                return {'error': "{0}".format(e)}

    def sync_request(self, method, url, payload=None, headers=None):
        return self.request(method, url, payload, headers)
