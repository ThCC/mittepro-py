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
import os
import base64
import unittest
from models import Mail, SearchMailArgs
from client import MittePro


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.server_uri_test = None
        self.variables = {
            "recipients": [
                "Foo Bar <foo.bar@gmail.com>",
                "Fulano Aquino <fulano@gmail.com>",
                "<ciclano@gmail.com>"
            ],
            "context_per_recipient": {
                "foo.bar@gmail.com": {"foo": True},
                "fulano.arquino@gmail.com.br": {"bar": True}
            },
            "from_": 'Beutrano <beutrano@mail.com>',
            "from_2": '<beutrano@mail.com>',
            "template_slug": 'test-101',
            "message_text": "Using this message instead.",
            "message_html": "<em>Using this message <strong>instead</strong>.</em>",
            "key": '2e7be7ced03535958e35',
            "secret": 'ca3cdba202104fd88d01',
            "files_names": [
                # 'foo.pdf',
                # 'bar.jpg',
                # 'foo_bar.txt',
            ]
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

        self.mittepro = MittePro(key=self.variables['key'], secret=self.variables['secret'], fail_silently=False,
                                 server_uri=self.server_uri_test, timeout_read=20)

    def get_attachments(self):
        attachments = []
        files = self.variables['files_names']
        for dfile in files:
            content = base64.encodestring(open(
                os.path.join(os.path.expanduser('~'), 'test_files', dfile), 'rb'
            ).read())
            attachments.append({'file': content, 'name': dfile})
        return attachments

    def test_method_post_text(self):
        # attachments = []
        # attachments = self.get_attachments()
        mail = Mail(
            recipient_list=self.variables['recipients'],
            message_text='Mah oia só https://pypi.org/',
            # remove comment if you gonna tested
            # message_html=self.variables["message_html"],
            from_=self.variables['from_'],
            # batchs=self.variables['batchs'],
            # time_between_batchs=self.variables['time_between_batchs'],
            subject="Just a test - Sended From_ Client AT 09",
            send_at='2018-11-16 10:45',
            # send_at='2018-02-05 09:32:00',
            activate_tracking=False,
            track_open=False,
            track_html_link=False,
            track_text_link=False,
            # attachments=attachments
        )
        response = self.mittepro.send(mail)
        print "response", response
        if response and 'emails_enviados' in response:
            self.assertGreater(len(response['emails_enviados']), 0)
        else:
            self.assertIsNotNone(response)

    def test_method_post_template(self):
        # attachments = []
        # attachments = self.get_attachments()
        mail = Mail(
            # headers={'X_CLIENT_ID': 1},
            recipient_list=self.variables['recipients'],
            # from_=self.variables['from_'],
            template_slug=self.variables['template_slug'],
            context={'foobar': True},
            context_per_recipient=self.variables['context_per_recipient'],
            subject="Just a test - Sended From Client AT 09",
            # remove comment if you gonna tested
            # message_text=self.variables["message_text"],
            # message_html=self.variables["message_html"],
            # use_tpl_default_subject=True,
            use_tpl_default_email=True,
            # use_tpl_default_name=True,
            # activate_tracking=True,
            # get_text_from_html=True,
            # attachments=attachments
        )
        # print mail.get_payload()
        response = self.mittepro.send_template(mail)
        print "response", response
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
