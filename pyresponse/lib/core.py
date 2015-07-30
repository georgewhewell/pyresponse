#!/usr/bin/env python
# coding=utf-8
#

class Core:

    api_username = None
    api_password = None

    api_context = None

    api_translator = None

    class Api:
        RPC_LITERAL_BRANDED = 'http://paint.pure360.com/paint.pure360.com/ctrlPaintLiteral.wsdl'
        RPC_LITERAL_UNBRANDED = 'http://emailapi.co.uk/emailapi.co.uk/ctrlPaintLiteral.wsdl'
        USERNAME = 'userName'
        PASSWORD = 'password'

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
        EVENT_NOTIFICATION = 'eventNotification'

    class Process:
        CREATE = 'create'
        STORE = 'store'
        SEARCH = 'search'
        LOAD = 'load'
        REMOVE = 'remove'
        INVALIDATE = 'logout'
        AUTHENTICATE = 'login'
        BATCH = 'getBatch'

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
        CUSTOM_FIELDS = 'existingCustomFieldNames'

    class Upload:
        TYPE = 'uploadTransactionType'
        APPEND = 'APPEND'
        PASTE_FILE = 'pasteFile'
        NOTIFY_URI = 'uploadFileNotifyEmail'
        NOTIFY_TYPE = 'uploadFileNotifyType'

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

    class Delivery:
        ID = 'deliveryId'

    class Notification:
        TYPES = 'notificationTypes'
        MAX = 'maxNotifications'
        MARK_AS_READ = ' markAsReadInd'
        CLICK = 'CLICK'
        OPEN = 'OPEN'


    def __init__(self, main):
        self.api_client = main.api_client
        self.api_translator = main.api_translator
        self.api_context = None


    def authenticate(self, api_username, api_password):
        """
        Retrieve a context id for a set of credentials, or throw a
        Core.AuthenticationError.
        ------------------------------------------------
        @param api_username              - username of account from which to make api calls
        @param api_password              - password of that same account
        @return result                   - self.api_context, having just been set
        """
        self.api_username = api_username
        self.api_password = api_password
        auth_response = self.make_request(Core.Class.CONTEXT,
                                          Core.Process.AUTHENTICATE, {Core.Api.USERNAME: api_username,
                                                                      Core.Api.PASSWORD: api_password})

        if not auth_response.get('ok'):
            message = ('Failed to authenticate credentials: api_username=%s, api_password=%s, response=%s' %
                       (self.api_username[:2] + 'xxx', self.api_password[:2] + 'xxx', self.api_translator.response_data(auth_response)))
            raise Core.AuthenticationError(message)
        self.api_context = self.api_translator.response_bean_id(auth_response, Core.Class.CONTEXT)
        return self.api_context


    def invalidate(self):
        """
        Clears authentication credentials, makes a logout call
        to PureResponse. Follow-on calls will fail before calling
        as a result of lacking an api context id (Core.context_id).
        ------------------------------------------------
        """
        self.make_request(Core.Class.CONTEXT, Core.Process.INVALIDATE, no_response=True)
        self.api_context = None
        self.api_password = None
        self.api_username = None


    def make_request(self, bean_class, bean_proc, entity_data=None, process_data=None, no_response=False):
        """
        Makes the actual SOAP requests.
        Translates entity and process data in the form of dictionaries
        into SOAP structures, using Translator.ensuds from ./translator.py.
        If the caller wants a response, return the SOAP response translated
        back into dictionary form.
        ------------------------------------------------
        @param bean_class                - describes the entity being operated on
        @param bean_proc                 - how to operate on the entity
        @param [entity_data]             - search parameters, identifying data, input
        @param [process_data]            - extra data for the process (create, store, load, ..)
                                           e.g. message name when sending a one to one message
        @return result                   - response dictionary, usually filtered before
                                           being returned by the API wrapper
        """
        if self.api_context or (bean_proc is Core.Process.AUTHENTICATE):
            response = self.api_client.service.handleRequest(self.api_context or self.api_translator.null(),
                                                             Core.Type.FACADE + '_' + bean_class,
                                                             bean_proc,
                                                             self.api_translator.ensuds(entity_data),
                                                             self.api_translator.ensuds(process_data))
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

    def get_batch(self, bean_class, process_data=None):
        return self.make_request(bean_class, Core.Process.BATCH, None, process_data)

    def create(self, bean_class, entity_data=None, process_data=None):
        """
        Proxy for create requests, fills in process parameter and filters
        the result returning only the bean id.
        ------------------------------------------------
        @param bean_class                - describes the entity being created
        @param [entity_data]             - input data for create process, almost always
                                           empty (see Helpers.send_to_person for exception)
        @param [process_data]            - process data for create process (exception as above)
        @return result                   - id of created object
        """
        create_response = self.make_request(bean_class, Core.Process.CREATE, entity_data, process_data)
        if not create_response.get('ok'):
            response_string = self.api_translator.response_data(create_response)
            if 'valid email address' in response_string:
                message = ('Invalid email address: %s' % (response_string))
                raise Core.InvalidEmailError(message)
            if 'action not allowed' in response_string:
                message = ('Not allowed: account likely missing api privelege, repsonse=%s' % (response_string))
                raise Core.NotAllowedError(message)
            message = ('Create failed: bean_class=%s, entity_data=%s, process_data=%s, response=%s' %
                       (bean_class, entity_data, process_data, response_string))
            raise Core.CreateError(message)
        return self.api_translator.response_bean_id(create_response, bean_class)


    def remove(self, bean_class, bean_id):
        """
        Proxy for remove request, fills in process parameter and data.
        Filters the result from Core.make_request before returning.
        ------------------------------------------------
        @param bean_class                - describes the entity being removed
        @param bean_id                   - specifies the bean id of the entity
        @return result                   - filtered response dictionary
        """
        remove_response = self.make_request(bean_class,
                                            Core.Process.REMOVE,
                                            {Core.Entity.ID: bean_id})
        if not remove_response.get('ok'):
            message = ('Remove failed: bean_class=%s, bean_id=%s, response=%s' %
                       (bean_class, bean_id, self.api_translator.response_data(remove_response)))
            raise Core.RemoveError(message)
        return self.api_translator.response_data(remove_response)


    def store(self, bean_class, entity_data):
        """
        Proxy for store request, fills in process parameter and
        filters the results.
        ------------------------------------------------
        @param bean_class                - describes the entity being stored
        @param entity_data               - entity data to store
        @return result                   - storage result e.g. {beanName: bus_entity_campaign_list}
        """
        store_response = self.make_request(bean_class, Core.Process.STORE, entity_data)
        if not store_response.get('ok'):
            response_string = str(self.api_translator.response_data(store_response))
            if 'already pending' in response_string:
                message = ('Already pending: response=%s' % (response_string))
                raise Core.PendingError(message)
            if 'marked as opted out' in response_string:
                message = ('Opted out: desired recipient has opted out, response=%s' % (response_string))
                raise Core.OptedOutError(message)
            message = ('Store failed: bean_class=%s, entity_data=%s, response=%s' %
                       (bean_class, entity_data, response_string))
            raise Core.StoreError(message)
        return self.api_translator.response_stored(store_response, bean_class)


    def search(self, bean_class, search_params):
        """
        Proxy for search request, fills in process parameter and
        filters the results.
        ------------------------------------------------
        @param bean_class                - describes the entity being searched for
        @param search_params             - dictionary of search parameters
        @return result                   - search results, list of found records
        """
        search_response = self.make_request(bean_class, Core.Process.SEARCH, search_params)
        if not search_response.get('ok'):
            message = ('Search failed: bean_class=%s, search_params=%s, response=%s' %
                       (bean_class, search_params, self.api_translator.response_data(search_response)))
            raise Core.SearchError(message)
        return self.api_translator.response_found(search_response, bean_class)


    def load(self, bean_class, entity_data):
        """
        Proxy for load request, fills in process parameter and
        filters the results.
        ------------------------------------------------
        @param bean_class                - describes the entity being loaded
        @param entity_data               - entity data to load from, e.g. {Core.List.ID: list_id}
        @return result                   - filtered result, dictionary of requested entity
        """
        load_response = self.make_request(bean_class, Core.Process.LOAD, entity_data)
        if not load_response.get('ok'):
            message = ('Load failed: bean_class=%s, entity_data=%s, response=%s' %
                       (bean_class, entity_data, self.api_translator.response_data(load_response)))
            raise Core.LoadError(message)
        return self.api_translator.response_data(load_response, Core.Type.ENTITY, bean_class)


    def load_search(self, bean_class, search_params):
        """
        Search for some parameters and for each resulting record,
        load said record and return the set of those results.
        ------------------------------------------------
        @param bean_class                - describes the entity being loaded
        @param search_params             - dictionary of search parameters
        @return result                   - list of dictionaries for loaded records
        """
        return [self.load(bean_class, entity_data) for entity_data in self.search(bean_class, search_params)]


    def filter_loaded(self, candidates, filters=None, output_filter=None):
        """
        Filter results of loading by some condition on a key, or filter
        the output. e.g. output_filter=Core.Filters.key_filter(Core.List.NAME)
        will take a list record and only return the list name field.
        ------------------------------------------------
        @param candidates                - list of records
        @param [filters]                 - dictionary of key, value
        @param [output_filter]           - filter each dictionary by some function,
                                           e.g. Core.Filters.key_filter
        @return result                   - filtered set of dictionaries
        """
        filtered = []
        for candidate in candidates:
            skip = False
            if candidate is None:
                continue
            if filters:
                for key, value in filters.iteritems():
                    # hands off!
                    candidate[key] = self.api_translator.htmldecode(self.api_translator.x_encode(candidate.get(key).unescape().__repr__()))
                    if isinstance(candidate.get(key), unicode) and isinstance(value, str):
                        value = value.decode('utf-8')
                    if not (candidate.get(key) == value):
                        skip = True
            if not skip:
                filtered.append(candidate if not output_filter else output_filter(candidate))
        return filtered


    def handle_existing(self, bean_class, found, overwrite_existing):
        """
        When creating a new record this function will handle existing records
        by the same name according to the value of overwrite_existing.
        ------------------------------------------------
        @param bean_class                - describes the entity being created
        @param found                     - set of existing records found
        @param overwrite_existing        - True/False, overwrite existing records?
        """
        if found:
            if overwrite_existing:
                removed = self.remove(bean_class, found.get(Core.Entity.ID))
            else:
                message = ('Record exists: overwrite_existing=%s' % (overwrite_existing))
                raise Core.ExistsError(message)


    class Filters:
        @staticmethod
        def key_filter(key):
            def filter(candidate):
                return candidate.get(key)
            return filter
        @staticmethod
        def keys_filter(keys):
            def filter(candidate):
                return dict([(key, candidate.get(key)) for key in keys if key in candidate])
            return filter

    class InvalidEmailError(Exception):
        pass

    class InvalidPersonError(Exception):
        pass

    class InvalidListError(Exception):
        pass

    class PendingError(Exception):
        pass

    class AuthenticationError(Exception):
        pass

    class NotAllowedError(Exception):
        pass

    class OptedOutError(Exception):
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

    class NoneFoundError(Exception):
        pass

    class ParameterError(Exception):
        pass

    class AccountLevelError(Exception):
        pass
