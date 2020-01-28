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
from client import MittePro
from models import Mail, SearchMailArgs


class TestMittePro(unittest.TestCase):
    def setUp(self):
        self.server_uri_test = None
        self.variables = {
            "recipients": [
                "Foo Bar <foo.bar@gmail.com>",
                "Fulano <fulano@gmail.com>",
                "<ciclano@gmail.com>"
            ],
            "context_per_recipient": {
                "foo.bar@gmail.com": {"foo": True},
                "fulano@gmail.com.br": {"bar": True}
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
                                 timeout_read=20)

    def get_attachments(self):
        attachments = []
        files = self.variables['files_names']
        for dfile in files:
            content = base64.encodebytes(open(
                os.path.join(os.path.expanduser('~'), 'test_files', dfile), 'rb'
            ).read())
            attachments.append({'file': content, 'name': dfile})
        return attachments

    def test_method_post_text(self):
        # attachments = []
        # attachments = self.get_attachments()
        mail = Mail(
            track_open=False,
            track_html_link=False,
            track_text_link=True,
            activate_tracking=False,
            subject='Mittepro-py client test',
            # send_at='2019-05-04 08:00:00',
            message_text=self.variables['message_text'],
            message_html=self.variables['message_html'],
            from_=self.variables['from_'],
            recipient_list=self.variables['recipients'],
            # context={'GMERGE': 'Mah oia Soh'},
            # context_per_recipient=self.variables['']
        )
        try:
            response = self.mittepro.send(mail)
            if response and 'emails_enviados' in response:
                self.assertGreater(len(response['emails_enviados']), 0)
            else:
                self.assertIsNotNone(response)
        except Exception as e:
            print("Exception", e)

    def t2est_method_post_template(self):
        # attachments = []
        # attachments = self.get_attachments()
        mail = Mail(
            track_open=True,
            track_html_link=False,
            track_text_link=False,
            activate_tracking=True,
            subject='Mittepro-py client test',
            send_at='2019-05-04 08:00:00',
            from_=self.variables['from_'],
            recipient_list=self.variables['recipients'],
            template_slug='tpl-teste',
            use_tpl_default_name=True,
            use_tpl_default_email=True,
            use_tpl_default_subject=True,
            context={'GMERGE': 'Mah oia Soh'},
            context_per_recipient=self.variables['context_per_recipient'],
            # attachments=attachments
        )
        # print mail.get_payload()
        response = self.mittepro.send_template(mail)
        print("response", response)
        if response and 'emails_enviados' in response:
            self.assertGreater(len(response['emails_enviados']), 0)
        else:
            self.assertIsNotNone(response)

    def t2est_method_get_mail_search(self):
        search_args = SearchMailArgs(
            end=self.search_variables['end'],
            start=self.search_variables['start'],
            app_cods=self.search_variables['app_ids'],
            # name_sender=self.search_variables['name_sender'],
            # email_sender=self.search_variables['email_sender'],
            # name_receiver=self.search_variables['name_receiver'],
            # template_slug=self.search_variables['template_slug'],
            # email_receiver=self.search_variables['email_receiver'],
        )
        response = self.mittepro.mail_search(search_args)
        if response and 'qtd_mails' in response and response['qtd_mails'] > 0:
            print("qtd_mails %s" % response['qtd_mails'])
            self.assertGreater(response['qtd_mails'], 0)
        else:
            print("Nothing found")
            self.assertIsNotNone(response)

    def t2est_method_get_mail_search_by_ids(self):
        response = self.mittepro.mail_search_by_ids(self.search_variables['uuids'])
        if response and len(response) > 0:
            print("uuids %s" % self.search_variables['uuids'])
            print("len(response) %s" % len(response))
            self.assertGreater(len(response), 0)
        else:
            print("Nothing found")
            self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
