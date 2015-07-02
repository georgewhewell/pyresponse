#!/usr/bin/env python
# coding=utf-8
#
from suds.client import Client as Suds

from .lib.core import Core
from .lib.translator import Translator
from .lib.helpers import Helpers

import types


class PureResponseClient(object):
    version = '1.2.7'

    api_client = None
    api_account_level = None

    api_core = None
    api_translator = None

    encoding_exceptions = [Core.Entity.ID,
                           Core.Message.ID,
                           Core.List.ID,
                           Core.Api.USERNAME,
                           Core.Api.PASSWORD]

    class AccountLevel:
        LITE = 10
        PRO = 20
        EXPERT = 40

    def __init__(self, api_version=Core.Api.RPC_LITERAL_UNBRANDED):
        self.api_client = Suds(api_version)
        self.api_translator = Translator(self)
        self.api_core = Core(self)

        self.register_helpers()


    def authenticate(self, api_username=None, api_password=None, api_account_level=AccountLevel.LITE):
        """
        Authenticates a username and password against the PureResponse API,
        must be done before making all other API calls.
        ------------------------------------------------
        @param api_username              - username of account from which to make api calls
        @param api_password              - password of that same account
        @param [api_account_level]       - your api account level indicates how many custom
                                           fields you are allowed to use in contact lists

                                           if you indicate a level higher than that of your
                                           account a pyresponse.Core.StoreErrors will be raised
                                           when your actual limit is met

                                           going over the limit indicated by this parameter will
                                           raise a pyresponse.Translator.AccountLevelError in
                                           those same cases

                                           pyresponse.AccountLevel.LITE offers 10 custom fields
                                           pyresponse.AccountLevel.PRO offers 20 custom fields
                                           pyresponse.AccountLevel.EXPERT offers 40 custom fields
        @return                          - bean id for a context bean in pureresponse, will be
                                           used to identify the API session
        """
        self.api_account_level = api_account_level
        if (not api_username) or (not api_password):
            message = ('Invalid authentication details: api_username=%s, api_password=%s' %
                       (api_username, api_password))
            raise Core.AuthenticationException(message)

        return self.api_core.authenticate(api_username, api_password)

    def invalidate(self):
        """
        Clears authentication credentials, makes a logout call
        to PureResponse. Follow-on calls will fail before calling
        as a result of lacking an api context id (Core.context_id).
        ------------------------------------------------
        """
        self.api_core.invalidate()


    def register_helpers(self):
        """
        Gives access to classes and methods from ./lib/helpers.py and
        ./lib/core.py from pyresponse.py, making the code a litle easier
        to maintain. Separates public facing interfaces from those mainly
        intended for internal use.
        ------------------------------------------------
        """
        for key, value in Helpers.__dict__.iteritems():
            if callable(value):
                setattr(self, key, types.MethodType(value, self))

        for key, value in Core.__dict__.iteritems():
            if isinstance(value, (type, types.ClassType)):
                setattr(self, key, value)
