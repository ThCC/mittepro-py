# -*- coding: utf-8 -*-
import re
import arrow
import base64
from datetime import datetime
from mitte_exceptions import InvalidParam
from utils import item_in_dict, item_not_in_dict, attr_in_instance, attr_not_in_instance


class Mail(object):
    TRACK_EMAIL_REGEX = re.compile(r"<.*?(.*).*>")
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    def __init__(self, **kwargs):
        assert 'from_' in kwargs or item_in_dict(kwargs, 'use_tpl_default_email'), \
            'Impossível enviar email sem o parâmetro "from". É preciso fornecer o parâmetro "from" ou ' \
            '"use_tpl_default_email"'
        assert 'recipient_list' in kwargs and len(kwargs.get('recipient_list')), \
            'Impossível enviar um email sem uma lista de destinatários'
        assert 'subject' in kwargs or item_in_dict(kwargs, 'use_tpl_default_subject'), \
            'Impossível enviar um email sem um assunto'

        # General mail vars
        self.set_attr('tags', kwargs)
        self.set_attr('headers', kwargs)
        self.set_attr('recipient_list', kwargs)
        self.set_attr('send_at', kwargs)
        self.set_attr('subject', kwargs)
        self.set_attr('from_', kwargs)
        self.set_attr('message_text', kwargs)
        self.set_attr('message_html', kwargs)
        self.set_attr('activate_tracking', kwargs)
        self.set_attr('track_open', kwargs)
        self.set_attr('track_html_link', kwargs)
        self.set_attr('track_text_link', kwargs)
        self.set_attr('get_text_from_html', kwargs)

        # Template mail vars
        self.set_attr('context', kwargs)
        self.set_attr('template_slug', kwargs)
        self.set_attr('use_tpl_default_name', kwargs)
        self.set_attr('use_tpl_default_email', kwargs)
        self.set_attr('use_tpl_default_subject', kwargs)
        self.set_attr('context_per_recipient', kwargs)

        self.validate_send_at(kwargs)
        self.check_from()
        self.check_recipient_list()

    def validate_send_at(self, kwargs):
        send_at = kwargs.get('send_at')
        if not send_at:
            return True
        try:
            datetime.strptime(send_at, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise InvalidParam(message_values=("'send_at'", 'Formato inválido, esperado: YYYY-mm-dd HH:MM:SS'))

        date_target = arrow.get(send_at + '-03:00', 'YYYY-MM-DD HH:mm:ssZZ')
        if arrow.now(tz='America/Sao_Paulo') <= date_target:
            return True
        raise InvalidParam(message_values=("'send_at'", 'O valor para data tem que ser maior do que a atual'))

    def set_attr(self, attr, kwargs):
        if attr in kwargs:
            setattr(self, attr, kwargs.get(attr))

    def __track_email(self, value):
        tracked = self.TRACK_EMAIL_REGEX.search(value)
        if tracked:
            return tracked.group(1)
        return None

    def __validate_email(self, value):
        email = self.__track_email(value)
        valid = self.EMAIL_REGEX.match(email)
        return valid is not None

    def __validate_recipient(self, value):
        email = self.__track_email(value)
        return email is not None

    def check_from(self):
        if not hasattr(self, 'from_'):
            return True
        if not getattr(self, 'from_'):
            delattr(self, 'from_')
            return True

        if not self.__validate_recipient(getattr(self, 'from_')):
            raise InvalidParam(message_values=(
                "'from_'", "O formato esperado ('nome <email>'; ou '<email>') não foi encontrado"
            ))
        if not self.__validate_email(getattr(self, 'from_')):
            raise InvalidParam(message_values=(
                "'from_'", "O endereço de e-mail do parâmetro 'from_' está inválido"
            ))

    def check_recipient_list(self):
        for recipient in getattr(self, 'recipient_list'):
            if not self.__validate_recipient(recipient):
                raise InvalidParam(message_values=(
                    "'recipient_list'", "O formato esperado ('nome <email>'; ou '<email>') não foi encontrado"
                ))
            if not self.__validate_email(recipient):
                raise InvalidParam(message_values=(
                    "'recipient_list'", "O item '{0}' contém um endereço de e-mail inválido".format(recipient)))

    def get_payload(self, endpoint='text'):
        if endpoint == 'template':
            if attr_not_in_instance(self, 'template_slug') and attr_not_in_instance(self, 'message_html'):
                raise AssertionError("Impossível enviar um email com template sem o conteúdo html. Ou você fornece "
                                     "o 'template_slug' ou o 'message_html'")
            if ((attr_in_instance(self, 'use_tpl_default_subject') or
                 attr_in_instance(self, 'use_tpl_default_email') or
                 attr_in_instance(self, 'use_tpl_default_name')) and
                    (attr_not_in_instance(self, 'template_slug'))):
                raise AssertionError("Impossível usar os recursos de um template, sem fornecer o 'template_slug'")
        else:
            if attr_not_in_instance(self, 'message_html') and attr_not_in_instance(self, 'message_text'):
                raise AssertionError('Impossível enviar um email sem conteúdo. É preciso fornecer um dos parâmetros '
                                     '"message_text" ou "message_html"')

        payload = self.__dict__
        if 'from_' in payload and payload['from_']:
            payload['from'] = payload['from_'].strip()
            del payload['from_']
        payload['sended_by'] = 4

        return payload


class SearchMailArgs(object):
    def __init__(self, **kwargs):
        if item_not_in_dict(kwargs, 'app_cods'):
            raise AssertionError("Parâmetro 'app_cods' não foi fornecido.")
        if item_not_in_dict(kwargs, 'start'):
            raise AssertionError("Parâmetro 'start' não foi fornecido.")
        if item_not_in_dict(kwargs, 'end'):
            raise AssertionError("Parâmetro 'end' não foi fornecido.")

        self.set_attr('end', kwargs)
        self.set_attr('start', kwargs)
        self.set_attr('status', kwargs)
        self.set_attr('app_cods', kwargs)
        self.set_attr('name_sender', kwargs)
        self.set_attr('email_sender', kwargs)
        self.set_attr('template_slug', kwargs)
        self.set_attr('name_receiver', kwargs)
        self.set_attr('email_receiver', kwargs)

    def set_attr(self, attr, kwargs):
        if attr in kwargs:
            setattr(self, attr, kwargs.get(attr))

    def get_payload(self):
        return self.__dict__
