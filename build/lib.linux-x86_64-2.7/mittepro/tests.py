# coding=utf-8
try:
    from test_variables import server_uri_test
except ImportError:
    server_uri_test = False
try:
    from test_variables import search_variables
except ImportError:
    search_variables = False
try:
    from test_variables import variables
except ImportError:
    variables = False
import unittest
from models import Mail, SearchMailArgs
from client import MittePro


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.server_uri_test = None
        self.variables = {
            "recipients": [
                "Foo Bar <foo.bar@gmail.com>",
                "Fulano Aquino <fulano.aquino@gmail.com>",
                "<ciclano.norego@gmail.com>"
            ],
            "context_per_recipient": {
                "foo.bar@gmail.com": {"foo": True},
                "fulano.arquino@gmail.com.br": {"bar": True}
            },
            "from_name": 'Beutrano',
            "from_email": 'beutrano@gmail.com',
            "template_slug": 'test-101',
            "message_text": "Using this message instead.",
            "message_html": "<em>Using this message <strong>instead</strong>.</em>",
            "key": '2e7be7ced03535958e35',
            "secret": 'ca3cdba202104fd88d01'
        }
        self.search_variables = {
            'app_ids': '1001',
            'start': '2017-10-26',
            'end': '2017-10-27',
            'uuids': [
                '21da05e09a214bf',
                '7b9332128a3f461',
                '09f7ceac90fe4b3',
                '0f39a611031c4ff',
                'f2412b7062814de'
            ]
        }

        if variables:
            self.variables = variables
        if server_uri_test:
            self.server_uri_test = server_uri_test
        if search_variables:
            self.search_variables = search_variables

        self.mittepro = MittePro(key=self.variables['key'], secret=self.variables['secret'],
                                 server_uri=self.server_uri_test, timeout_read=5)

    def test_method_post_text(self):
        mail = Mail(
            recipient_list=self.variables['recipients'],
            message_text='Mah oia só https://pypi.org/',
            # remove comment if you gonna tested
            # message_html=self.variables["message_html"],
            from_name=self.variables['from_name'],
            from_email=self.variables['from_email'],
            subject="Just a test - Sended From Client AT 09",
            # send_at='2018-02-05 09:32:00',
            activate_tracking=False,
            track_open=True,
            track_html_link=True,
            track_text_link=True,
        )
        response = self.mittepro.send(mail)
        if response and 'emails_enviados' in response:
            self.assertGreater(len(response['emails_enviados']), 0)
        else:
            self.assertIsNotNone(response)

    def test_method_post_template(self):
        mail = Mail(
            headers={'X_CLIENT_ID': 1},
            recipient_list=self.variables['recipients'],
            from_name=self.variables['from_name'],
            from_email=self.variables['from_email'],
            template_slug=self.variables['template_slug'],
            context={'foobar': True},
            context_per_recipient=self.variables['context_per_recipient'],
            # remove comment if you gonna tested
            # message_text=self.variables["message_text"],
            # message_html=self.variables["message_html"],
            use_tpl_default_subject=True,
            use_tpl_default_email=True,
            use_tpl_default_name=True,
            activate_tracking=True,
            get_text_from_html=True
        )
        response = self.mittepro.send_template(mail)
        if response and 'emails_enviados' in response:
            self.assertGreater(len(response['emails_enviados']), 0)
        else:
            self.assertIsNotNone(response)

    def test_method_get_mail_search(self):
        search_args = SearchMailArgs(
            app_ids=self.search_variables['app_ids'],
            start=self.search_variables['start'],
            end=self.search_variables['end']
        )
        response = self.mittepro.mail_search(search_args)
        if response and len(response) > 0:
            self.assertGreater(len(response), 0)
        else:
            self.assertIsNotNone(response)

    def test_method_get_mail_search_by_ids(self):
        response = self.mittepro.mail_search_by_ids(self.search_variables['uuids'])
        if response and len(response) > 0:
            self.assertGreater(len(response), 0)
        else:
            self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
