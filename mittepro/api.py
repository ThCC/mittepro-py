import json
import arrow
import logging
import requests
from utils import is_json
from mitte_exceptions import APIError, TimeoutError
from apysignature.query_encoder import QueryEncoder
from apysignature.signature import Request as Request_sig, Token
from requests import Request, Session, ReadTimeout, ConnectTimeout, HTTPError

__version__ = '2.2.1'
logging.basicConfig(format='%(asctime)s %(message)s')


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
        for key, value in payload.items():
            url += QueryEncoder.encode_param(key, str(value)) + '&'
        return url.rstrip('&')

    def sign_request(self, auth_timestamp=None):
        request = Request_sig(self.http_method, self.endpoint, {})
        token = Token(self._api_key, self._api_secret)
        auth = request.sign(token, auth_timestamp)
        return auth

    def correct_auth_timestamp(self, msg_error, payload):
        substring = 'Server time: '
        server_timestamp = msg_error[msg_error.index(substring) + len(substring):]
        server_arw = arrow.get(int(server_timestamp))
        right_timestamp = arrow.now().replace(hour=int(server_arw.format('HH'))).timestamp
        return self.request(payload=payload, auth_timestamp=right_timestamp)

    def send_request(self, url, payload):
        if payload and self.http_method == 'GET':
            response = requests.get(url, payload)
        else:
            request = Request(
                self.http_method, url,
                json=payload,
                headers=self.headers
            )
            prepped = request.prepare()
            timeout = (10, self.timeout_read)
            response = self._session.send(prepped, timeout=timeout)

        valid_codes = (200, 201)
        if hasattr(response, 'status'):
            status_code = response.status
        else:
            status_code = response.status_code

        if response and status_code in valid_codes and response.text:
            return json.loads(response.text)
        else:
            logging.info("EXTERNAL API: request error: {0}".format(response.reason))
            if is_json(response.text):
                content = json.loads(response.text)
                msg = content['error'] if 'error' in content else content['detail']
            else:
                msg = response.text[0:response.text.index('Request Method')].strip()
            if 'Timestamp expired' in msg:
                return self.correct_auth_timestamp(msg, payload)
            elif not self.fail_silently:
                raise APIError(message_values=(msg.encode('utf8'),))
            else:
                return {'error': msg.encode('utf8')}

    def request(self, payload=None, auth_timestamp=None):
        url = self.server_uri + self.endpoint
        # Generate and sign request URL
        auth = self.sign_request(auth_timestamp)
        if auth:
            url = self.query_encode(url, auth)

        logging.info('EXTERNAL API: sending request on {0}'.format(url))
        try:
            return self.send_request(url, payload)
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
