#!/usr/bin/env python
# coding=utf-8
#

from suds.client import Client as Suds

class Core:

    api_username = None
    api_password = None

    api_context = None

    api_translator = None

    class Type:
        ENTITY = 'bus_entity'
        FACADE = 'bus_facade'
        SEARCH = 'bus_search'

    class Class:
        CONTEXT = 'context'
        CAMPAIGN_EMAIL = 'campaign_email'
        CAMPAIGN_DELIVERY = 'campaign_delivery'
        CAMPAIGN_AUTOMATION = 'campaign_automation'
        CAMPAIGN_ONE_TO_ONE = 'campaign_one2one'
        CAMPAIGN_LIST = 'campaign_list'
        CAMPAIGN_FILTER = 'campaign_filter'
        CAMPAIGN_SMS = 'campaign_sms'
        CAMPAIGN_PERSON = 'campaign_person'

    class Process:
        CREATE = 'create'
        STORE = 'store'
        SEARCH = 'search'
        LOAD = 'load'
        REMOVE = 'remove'
        INVALIDATE = 'logout'
        AUTHENTICATE = 'login'

    class Entity:
        ID = 'beanId'

    class Message:
        ID = 'messageId'
        NAME = 'messageName'
        MSG_NAME = 'message_messageName'
        SUBJECT = 'subject'
        BODY_HTML = 'bodyHtml'
        TO_ADDRESS = 'toAddress'
        CUSTOM_DATA = 'customData'

    class List:
        ID = 'listId'
        IDS = 'listIds'
        NAME = 'listName'

    class Upload:
        TYPE = 'uploadTransactionType'
        NOTIFY_URI = 'uploadFileNotifyEmail'
        PASTE_FILE = 'pasteFile'

    class Person:
        EMAIL = 'email'
        MOBILE = 'mobile'
        ID = 'personId'

    class Scheduling:
        DELIVERY_TIME = 'deliveryDtTm'
        MINUTES = 'minutes'
        HOURS = 'hours'
        DAYS = 'days'

    class Result:
        FOUND = 'idData'
        RESULT = 'result'
        RESULT_DATA = 'resultData'


    def __init__(self, main):
        self.api_client = main.api_client
        self.api_translator = main.api_translator
        self.api_context = None


    def authenticate(self, api_username, api_password):
        self.api_username = api_username
        self.api_password = api_password
        auth_response = self.make_request(Core.Type.FACADE,
                                          Core.Class.CONTEXT,
                                          Core.Process.AUTHENTICATE, {'userName': api_username,
                                                                      'password': api_password})

        if not auth_response.get('ok'):
            message = ('Failed to authenticate credentials: api_username=%s, api_password=%s, response=%s' %
                       (self.api_username, self.api_password, self.api_translator.response_data(auth_response)))
            raise Core.AuthenticationError(message)
        self.api_context = self.api_translator.response_bean_id(auth_response, Core.Class.CONTEXT)
        return self.api_context


    def invalidate(self):
        self.make_request(Core.Type.FACADE, Core.Class.CONTEXT, Core.Process.INVALIDATE, no_response=True)
        self.api_context = None
        self.api_password = None
        self.api_username = None


    def make_request(self, b_type, bean_class, b_proc, entity_data=None, p_data=None, no_response=False):
        if self.api_context or (b_proc is Core.Process.AUTHENTICATE):
            response = self.api_client.service.handleRequest(self.api_context or self.api_translator.null(),
                                                             b_type + '_' + bean_class,
                                                             b_proc,
                                                             self.api_translator.ensuds(entity_data),
                                                             self.api_translator.ensuds(p_data))
            if no_response:
                return {'ok': True}
            else:
                result = self.api_translator.desuds(response)
                result['ok'] = result.get('ok', False)
                return result
        else:
            message = ('Not authenticated: api_context=%s for api_username=%s, api_password=%s' %
                       (self.api_context, self.api_username, self.api_password))
            raise Core.AuthenticationError(message)


    def create(self, bean_class, entity_data=None, process_data=None):
        create_response = self.make_request(Core.Type.FACADE, bean_class, Core.Process.CREATE, entity_data, process_data)
        if not create_response.get('ok'):
            message = ('Create failed: bean_class=%s, entity_data=%s, process_data=%s, response=%s' %
                       (bean_class, entity_data, process_data, self.api_translator.response_data(create_response)))
            raise Core.CreateError(message)
        return self.api_translator.response_bean_id(create_response, bean_class)


    def remove(self, bean_class, bean_id):
        remove_response = self.make_request(Core.Type.FACADE, bean_class,
                                            Core.Process.REMOVE,
                                            {Core.Entity.ID: bean_id})
        if not remove_response.get('ok'):
            message = ('Remove failed: bean_class=%s, bean_id=%s, response=%s' %
                       (bean_class, bean_id, self.api_translator.response_data(remove_response)))
            raise Core.RemoveError(message)
        return self.api_translator.response_data(remove_response)


    def store(self, bean_class, entity_data):
        store_response = self.make_request(Core.Type.FACADE, bean_class, Core.Process.STORE, entity_data)
        if not store_response.get('ok'):
            message = ('Store failed: bean_class=%s, entity_data=%s, response=%s' %
                       (bean_class, entity_data, self.api_translator.response_data(store_response)))
            raise Core.StoreError(message)
        return self.api_translator.response_data(store_response)


    def search(self, bean_class, search_params):
        search_response = self.make_request(Core.Type.FACADE, bean_class, Core.Process.SEARCH, search_params)
        if not search_response.get('ok'):
            message = ('Search failed: bean_class=%s, search_params=%s, response=%s' %
                       (bean_class, search_params, self.api_translator.response_data(search_response)))
            raise Core.SearchError(message)
        return self.api_translator.response_found(search_response, bean_class)


    def load(self, bean_class, entity_data):
        load_response = self.make_request(Core.Type.FACADE, bean_class, Core.Process.LOAD, entity_data)
        if not load_response.get('ok'):
            message = ('Load failed: bean_class=%s, entity_data=%s, response=%s' %
                       (bean_class, entity_data, self.api_translator.response_data(load_response)))
            raise Core.LoadError(message)
        return self.api_translator.response_data(load_response, Core.Type.ENTITY, bean_class)


    def load_search(self, bean_class, search_params):
        return [self.load(bean_class, entity_data) for entity_data in self.search(bean_class, search_params)]


    def filter_loaded(self, candidates, filters=None, output_filter=None):
        filtered = []
        for candidate in candidates:
            skip = False
            if candidate is None:
                continue
            if filters:
                for key, value in filters.iteritems():
                    if not candidate.get(key) == value:
                        skip = True
            if not skip:
                filtered.append(candidate if not output_filter else output_filter(candidate))
        return filtered


    def handle_existing(self, bean_class, found, overwrite_existing):
        if found and len(found):
            if overwrite_existing:
                removed = self.remove(bean_class, found[0].get(Core.Entity.ID))
            else:
                message = ('Record exists: overwrite_existing=%s' % (overwrite_existing))
                raise Core.ExistsError(message)


    class Filters:
        @staticmethod
        def key_filter(key):
            def filter(candidate):
                return candidate.get(key)
            return filter


    class AuthenticationError(Exception):
        pass

    class CreateError(Exception):
        pass

    class RemoveError(Exception):
        pass

    class StoreError(Exception):
        pass

    class SearchError(Exception):
        pass

    class LoadError(Exception):
        pass

    class ExistsError(Exception):
        pass
