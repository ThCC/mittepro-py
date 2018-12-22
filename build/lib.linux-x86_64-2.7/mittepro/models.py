# -*- coding: utf-8 -*-
import re
import arrow
import base64
from datetime import datetime
from mittepro.exceptions import InvalidParam
from mittepro import item_in_dict, item_not_in_dict, attr_in_instance, attr_not_in_instance


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
        self.batch_min_size = 2
        self.batch_min_time = 5
        self.total_email_limit = 500
        self.attach_size_limit_mb = 10
        self.attach_size_limit_b = self.attach_size_limit_mb * 1024 * 1024

        # General mail vars
        self.set_attr('tags', kwargs)
        self.set_attr('batchs', kwargs)
        self.set_attr('headers', kwargs)
        self.set_attr('recipient_list', kwargs)
        self.set_attr('time_between_batchs', kwargs)
        self.set_attr('recipients_per_batchs', kwargs)
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
        self.set_attr('attachments', kwargs)

        # Template mail vars
        self.set_attr('context', kwargs)
        self.set_attr('template_slug', kwargs)
        self.set_attr('use_tpl_default_name', kwargs)
        self.set_attr('use_tpl_default_email', kwargs)
        self.set_attr('use_tpl_default_subject', kwargs)
        self.set_attr('context_per_recipient', kwargs)

        self.check_batchs_args()
        self.validate_send_at(kwargs)
        self.check_from()
        self.check_recipient_list()
        self.check_attachments()

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
                    "'recipient_list'", "O item '{0}' contém um endereço de e-mail inválido".format(recipient)
                ))

        system_takes_over_batchs = None
        batchs = getattr(self, 'batchs', None)
        headers = getattr(self, 'headers', None)
        if headers:
            if 'system_takes_over_batchs' in headers and headers['system_takes_over_batchs']:
                system_takes_over_batchs = headers['system_takes_over_batchs']

        total_recipients = len(getattr(self, 'recipient_list'))
        if total_recipients > self.total_email_limit and batchs is None and system_takes_over_batchs is None:
            raise InvalidParam(message_values=(
                'recipient_list',
                'Não é possível enviar mais de {0} de contatos sem fornecer o parâmetro '
                '"batch" com o mínimo valor de 2'.format(self.total_email_limit)
            ))

    def check_attachment_size(self, file_size, attach_name=None):
        if file_size >= self.attach_size_limit_b:
            diff = file_size - self.attach_size_limit_b
            diff = '%.2f' % (diff / float(1000 * 1000))
            if attach_name:
                'O tamanho '
                message = """O tamanho de um dos anexos ultrapassa o limite de {0} MB permitido. O arquivo '{1}'
                supera em {2} MB""".format(
                    self.attach_size_limit_mb, attach_name, diff)
            else:
                message = """A soma do tamanho dos anexos ultrapassa o limite de {0} MB permitido.
                O total supera em {1} MB""".format(self.attach_size_limit_mb, diff)
            raise InvalidParam(message_values=("'attachments'", message))

    def check_attachments(self):
        if not hasattr(self, 'attachments'):
            return True
        if not getattr(self, 'attachments'):
            delattr(self, 'attachments')
            return True
        if not isinstance(getattr(self, 'attachments'), list):
            raise InvalidParam(
                message_values=(
                    "'attachments'",
                    "Attachments should be a List of dictionaries. Like: [{name: 'foo.bar', file: 'bWl0dGVwcm8=\n'}]"
                ))
        total_attachs_size = 0
        for attach in getattr(self, 'attachments'):
            if not isinstance(attach, dict):
                raise InvalidParam(
                    message_values=(
                        "'attachments'",
                        "Attachments should be a List of dictionaries. "
                        "Like: [{name: 'foo.bar', file: 'bWl0dGVwcm8=\n'}]"
                    ))
            if 'name' not in attach:
                raise InvalidParam(
                    message_values=(
                        "'attachments'",
                        "Attachment should have an name. Like: {name: 'foo.bar', file: 'bWl0dGVwcm8=\n'}"
                    ))
            if 'file' not in attach:
                raise InvalidParam(
                    message_values=(
                        "'attachments'",
                        "Attachment should have the contents of the file in base64. "
                        "Like: {name: 'foo.bar', file: 'bWl0dGVwcm8=\n'}"
                    ))
            try:
                dfile = base64.decodestring(attach['file'])
            except TypeError:
                raise InvalidParam(message_values=("'attachments'", 'Attachment file should be in base64.'))
            file_size = len(dfile)
            self.check_attachment_size(file_size, attach['name'])
            total_attachs_size += file_size
        self.check_attachment_size(total_attachs_size)

    def check_batchs_args(self):
        batchs = getattr(self, 'batchs', None)
        headers = getattr(self, 'headers', {})
        time_between_batchs = getattr(self, 'time_between_batchs', None)
        recipients_per_batchs = getattr(self, 'recipients_per_batchs', None)

        if not batchs and not time_between_batchs and not recipients_per_batchs:
            return True

        if not time_between_batchs:
            raise InvalidParam(message_values=(
                'time_between_batchs', 'O parâmetro não foi fornecido ou o valor é inválido'
            ))
        if time_between_batchs < self.batch_min_time:
            raise InvalidParam(message_values=('time_between_batchs', 'O parâmetro está com um valor menor que 5'))

        temp_time = int(time_between_batchs)
        time_between_batchs = self.batch_min_time * (temp_time / self.batch_min_time)

        if not time_between_batchs:
            raise InvalidParam(message_values=(
                'time_between_batchs', 'O parâmetro "time_between_batchs" está com um valor menor que 5'
            ))
        setattr(self, 'time_between_batchs', time_between_batchs)

        if headers and item_in_dict(headers, 'system_takes_over_batchs'):
            return True

        if not batchs and not recipients_per_batchs:
            raise InvalidParam(
                message="MitteProError - Parâmetros {0} são inválidos. Razão: {1}",
                message_values=(
                    'batchs e recipients_per_batchs',
                    'Não é possível enviar mais de {0} de contatos sem fornecer o parâmetro "batch" '
                    'ou o "recipients_per_batch" com o mínimo valor de 2'.format(self.total_email_limit)
                ))

        total_recipients = len(getattr(self, 'recipient_list'))
        if recipients_per_batchs:
            if recipients_per_batchs < self.batch_min_size:
                raise InvalidParam(message_values=(
                    'recipients_per_batchs', 'O parâmetro está com um valor menor que 2'))
            try:
                recipients_per_batchs = int(recipients_per_batchs)
                if not recipients_per_batchs:
                    raise InvalidParam(message_values=(
                        'recipients_per_batchs', 'O parâmetro não foi fornecido ou o valor é inválido'))
            except ValueError:
                raise InvalidParam(message_values=(
                    'recipients_per_batchs', 'O parâmetro não foi fornecido ou o valor é inválido'))
            if recipients_per_batchs > total_recipients:
                raise InvalidParam(message_values=(
                    'recipients_per_batchs',
                    'O valor do parâmetro "recipients_per_batchs" é maior que a quantidade de destinatários'
                ))
            setattr(self, 'recipients_per_batchs', recipients_per_batchs)
        elif batchs:
            if batchs < self.batch_min_size:
                raise InvalidParam(message_values=('batchs', 'O parâmetro está com um valor menor que 2'))
            try:
                batchs = int(batchs)
                if not batchs:
                    raise InvalidParam(message_values=('batchs', 'O parâmetro não foi fornecido ou o valor é inválido'))
            except ValueError:
                raise InvalidParam(message_values=('batchs', 'O parâmetro não foi fornecido ou o valor é inválido'))
            batchs_size = total_recipients / batchs
            if batchs_size > self.total_email_limit:
                raise InvalidParam(message_values=(
                    'batchs', 'O tamanho dos lotes ("batchs") supera o limite '
                              'de {0} e-mails'.format(self.total_email_limit)
                ))

            remaining = total_recipients % batchs
            last_batch_plus_one = item_in_dict(headers, 'last_batch_plus_one')

            if remaining and last_batch_plus_one:
                return True

            if batchs_size * batchs != total_recipients:
                raise InvalidParam(message_values=(
                    'batchs',
                    'A distribuição entre os lotes está inválida, provavelmente a quantidade de '
                    'destinatários não é multiplo da quantidade de lotes'
                ))
            setattr(self, 'batchs', batchs)
        else:
            raise InvalidParam(
                message="MitteProError - Parâmetros {0} são inválidos. Razão: {1}",
                message_values=(
                    'batchs e recipients_per_batchs',
                    'Não é possível enviar mais de {0} de contatos sem fornecer o parâmetro "batch" '
                    'ou o "recipients_per_batch" com o mínimo valor de 2'.format(self.total_email_limit)
                ))

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
            if attr_not_in_instance(self, 'attachments') and \
                    attr_not_in_instance(self, 'message_html') and \
                    attr_not_in_instance(self, 'message_text'):
                raise AssertionError('Impossível enviar um email sem conteúdo. É preciso fornecer um dos parâmetros '
                                     '"message_text", "message_html" ou "attachments"')

        payload = self.__dict__
        if 'from_' in payload and payload['from_']:
            payload['from'] = payload['from_'].strip()
            del payload['from_']
        payload['sended_by'] = 4

        return payload


class SearchMailArgs(object):
    def __init__(self, **kwargs):
        if item_not_in_dict(kwargs, 'app_ids'):
            raise AssertionError("Parâmetro 'app_ids' não foi fornecido.")
        if item_not_in_dict(kwargs, 'start'):
            raise AssertionError("Parâmetro 'start' não foi fornecido.")
        if item_not_in_dict(kwargs, 'end'):
            raise AssertionError("Parâmetro 'start' não foi fornecido.")

        self.set_attr('end', kwargs)
        self.set_attr('start', kwargs)
        self.set_attr('status', kwargs)
        self.set_attr('appIds', kwargs)
        self.set_attr('nameSender', kwargs)
        self.set_attr('emailSender', kwargs)
        self.set_attr('templateSlug', kwargs)
        self.set_attr('nameReceiver', kwargs)
        self.set_attr('emailReceiver', kwargs)

    def set_attr(self, attr, kwargs):
        if attr in kwargs:
            setattr(self, attr, kwargs.get(attr))

    def get_payload(self):
        return self.__dict__
