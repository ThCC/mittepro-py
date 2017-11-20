# -*- coding: utf-8 -*-
class BaseError(Exception):
    def __init__(self, message=None, codigo=None, message_values=()):
        self.message_values = message_values
        self.codigo = codigo
        super(Exception, self).__init__(message)


class InvalidParam(BaseError):
    def __init__(self, message="MitteProError - Parameter {0} is invalid. Reason: {1}", codigo=None, message_values=()):
        self.message_values = message_values
        self.codigo = codigo
        if message_values:
            message = message.format(*message_values)
        super(BaseError, self).__init__(message)


class APIError(BaseError):
    def __init__(self, message="MitteProError. Reason: {0}", codigo=None, message_values=()):
        self.message_values = message_values
        self.codigo = codigo
        if message_values:
            message = message.format(*message_values)
        super(BaseError, self).__init__(message)


class ImproperlyConfigured(BaseError):
    def __init__(self, message="MitteProError. Improper configuration. Reason: {0}", codigo=None, message_values=()):
        self.message_values = message_values
        self.codigo = codigo
        if message_values:
            message = message.format(*message_values)
        super(BaseError, self).__init__(message)
