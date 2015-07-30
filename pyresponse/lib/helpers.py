#!/usr/bin/env python
# coding=utf-8
#
import time
import datetime
import pytz
import csv
import StringIO
import base64

from .core import Core

NOTIFY_TYPE = 'http'
DEFAULT_NOTIFY_HTTP = 'http://example.com'
WAIT_INTERVAL = 10
WAIT_TIMEOUT = 60

UTC_TIMEZONE = pytz.timezone('Etc/UTC')
GMT_TIMEZONE = pytz.timezone('Europe/London')


class Helpers:

    def person_by_email(self, email_address, output_filter=None):
        """
        Get an (optionally filtered) person record from an email address.
        Note that person records will not include custom fields as these
        exist on a per-list basis.
        ------------------------------------------------
        @param email_address             - 'blackhole@exmaple.com'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.Person.ID)
                                           will ouput Core.Person.ID field instead of dictionary
        @return person                   - either a (optionally filtered) person record or None
        """
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_PERSON,
                                           {Core.Person.EMAIL: email_address})
        person = self.api_core.filter_loaded(loaded,
                                             {Core.Person.EMAIL: email_address},
                                             output_filter)
        return person[0] if len(person) else None


    def person_by_id(self, person_id, output_filter=None):
        """
        Get an (optionally filtered) person record from a person ID.
        Note that person records will not include custom fields as these
        exist on a per-list basis.
        ------------------------------------------------
        @param person_id                 - '555555555'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.Person.EMAIL)
                                           will ouput Core.Person.EMAIL field instead of dictionary
        @return person                   - either an (optionally filtered) person record or None
        """
        loaded = self.api_core.load(Core.Class.CAMPAIGN_PERSON, {Core.Person.ID: person_id})
        person = self.api_core.filter_loaded([loaded], None, output_filter)
        return person[0] if len(person) else None

    def wait_for_list(self, list_name, timeout=WAIT_TIMEOUT):
        timeout_at = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() < timeout_at:
          try:
            assert self.list_by_name(list_name)
            return
          except AssertionError as exception:
            time.sleep(WAIT_INTERVAL)
        raise Exception('List not found after {}s'.format(timeout))

    def list_by_name(self, list_name, output_filter=None):
        """
        Get an (optionally filtered) list record from a list name.
        ------------------------------------------------
        @param list_name                 - 'my_contact_list'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.List.ID)
                                           will ouput Core.List.ID field instead of dictionary
        @return list_                    - either an (optionally filtered) list record or None
        """
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_LIST,
                                           {Core.List.NAME: list_name})
        list_ = self.api_core.filter_loaded(loaded,
                                            {Core.List.NAME: list_name},
                                            output_filter)
        return list_[0] if len(list_) else None


    def list_by_id(self, list_id, output_filter=None):
        """
        Get an (optionally filtered) list record from a list id.
        ------------------------------------------------
        @param list_id                   - '555555'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.List.CUSTOM_FIELD_NAMES)
                                           will ouput Core.List.CUSTOM_FIELD_NAMES field instead
                                           of dictionary
        @return list_                    - either an (optionally filtered) list record or None
        """
        loaded = self.api_core.load(Core.Class.CAMPAIGN_LIST, {Core.List.ID: list_id})
        list_ = self.api_core.filter_loaded([loaded], None, output_filter)
        return list_[0] if len(list_) else None



    def filter_by_name(self, filter_name, output_filter=None):
        """
        Get an (optionally filtered) filter record from a filter name.
        ------------------------------------------------
        @param filter_name               - 'my_filter'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.Filter.ID)
                                           will ouput Core.Filter.ID field instead of dictionary
        @return filter                   - either an (optionally filtered) filter record or None
        """
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_FILTER,
                                           {Core.Filter.NAME: filter_name})
        filter_ = self.api_core.filter_loaded(loaded,
                                              {Core.Filter.NAME: filter_name},
                                              output_filter)
        return filter_[0] if len(filter_) else None

    def filter_by_id(self, filter_id, output_filter=None):
        """
        Get an (optionally filtered) filter record from a filter id.
        ------------------------------------------------
        @param filter_id                 - '55555'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.Filter.fieldNameList)
                                           will ouput Core.Filter.fieldNameList field instead
                                           of dictionary
        @return filter                   - either an (optionally filtered) filter record or None
        """
        loaded = self.api_core.load(Core.Class.CAMPAIGN_FILTER, {Core.Filter.ID: filter_id})
        filter_ = self.api_core.filter_loaded([loaded], None, output_filter)
        return filter_[0] if len(filter_) else None

    def filters_for_list_id(self, list_id, search_params=None, output_filter=None):
        """
        Get a set of (optionally filtered) filter records for a given list id.
        ------------------------------------------------
        @param list_id                   - '555555'
        @param [search_params]           - a dictionary of keys and values to match against
        @param [output_filter]           - filter for the records, e.g.
                                           Core.Filters.key_filter(Core.Filter.NAME) will output a
                                           set of values for the Core.Filter.NAME field instead of
                                           full filter records
        @return filters                  - a (potentially empty) set of (optionally filtered)
                                           filter records
        """
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_FILTER, {Core.List.ID: list_id})
        filters = self.api_core.filter_loaded(loaded, search_params, output_filter)
        return filters


    def message_by_name(self, message_name, output_filter=None):
        """
        Get an (optionally filtered) message record from a message name.
        ------------------------------------------------
        @param message_name              - 'my_message'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.Message.ID) will output
                                           the value of the Core.Message.ID field instead of a
                                           message record
        @return message                  - either an (optionally filtered) message record or None
        """
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_EMAIL,
                                           {Core.Message.NAME: message_name})
        message = self.api_core.filter_loaded(loaded,
                                              {Core.Message.NAME: message_name},
                                              output_filter)
        return message[0] if len(message) else None

    def message_by_id(self, message_id, output_filter=None):
        """
        Get an (optionally filtered) message record from a message id.
        ------------------------------------------------
        @param message_id                - '555555'
        @param [output_filter]           - filter for the record, e.g.
                                           Core.Filters.key_filter(Core.Message.BODY_HTML) will output
                                           the value of the Core.Message.BODY_HTML field instead of a
                                           full message record
        @return message                  - either an (optionally filtered) message record or None
        """
        loaded = self.api_core.load(Core.Class.CAMPAIGN_EMAIL, {Core.Message.ID: message_id})
        message = self.api_core.filter_loaded([loaded], None, output_filter)
        return message[0] if len(message) else None

    def create_message(self, message_name, subject, message_body, overwrite_existing=False):
        """
        Create an email message, optionally overwriting any existing
        records with the same message name.
        ------------------------------------------------
        @param message_name              - 'my_message'
        @param subject                   - 'subject line'
        @param message_body              - '<h1>Hello, world</h1>'
        @param [overwrite_existing]      - should existing records by this name be overwritten?
                                           True / False
        @return result                   - storage result e.g. {emailId: 555555,
                                                                beanName: bus_entity_campaign_email,
                                                                messageId: 555555}
        """
        self.api_core.handle_existing(Core.Class.CAMPAIGN_EMAIL,
                                      self.message_by_name(message_name),
                                      overwrite_existing)
        created = self.api_core.create(Core.Class.CAMPAIGN_EMAIL)
        entity_data = {Core.Message.NAME: message_name,
                       Core.Message.SUBJECT: subject,
                       Core.Message.BODY_HTML: message_body,
                       Core.Entity.ID: created}
        return self.api_core.store(Core.Class.CAMPAIGN_EMAIL, entity_data)


    def create_list(self, list_name, list_data, notify_uri=DEFAULT_NOTIFY_HTTP, overwrite_existing=False):
        """
        Create a contact list, optionally overwriting any existing
        records with the same message name.
        ------------------------------------------------
        @param list_name                 - 'my_contact_list'
        @param list_data                 - person record or list of person records e.g.
                                           {'email': 'blackhole@example.com', 'name': 'John Doe'}
        @param [notify_uri]              - email address to receive notification when finished
                                           e.g. 'blackhole+notifications@example.com'
        @param [overwrite_existing]      - should existing recods by this name be overwritten?
                                           True / False
        @return result                   - storage result e.g. {beanName: bus_entity_campaign_list}
        """
        self.api_core.handle_existing(Core.Class.CAMPAIGN_LIST,
                                      self.list_by_name(list_name),
                                      overwrite_existing)

        created = self.api_core.create(Core.Class.CAMPAIGN_LIST)
        paste_file = self.api_translator.encsv(list_data)

        entity_data = {
          Core.Upload.NOTIFY_URI: notify_uri,
          Core.Upload.NOTIFY_TYPE: NOTIFY_TYPE,
          Core.List.NAME: list_name,
          Core.Entity.ID: created
        }
        entity_data.update([self.api_translator.base_encode(Core.Upload.PASTE_FILE, paste_file)])
        entity_data.update(self.api_translator.csv_fields(paste_file))
        return self.api_core.store(Core.Class.CAMPAIGN_LIST, entity_data)


    def send_to_person(self, message_name, email_address, custom_data=None):
        """
        Send a one off transactional email message to a given
        email address.
        ------------------------------------------------
        @param message_name              - 'my_message'
        @param email_address             - 'blackhole@example.com'
        @param [custom_data]             - dictionary of merge variables for the email
        @return result                   - storage result e.g. {beanName: bus_entity_campaign_one2one}
        """
        entity_data = {Core.Message.TO_ADDRESS: email_address}
        if custom_data is not None:
            entity_data[Core.Message.CUSTOM_DATA] = custom_data
        try:
            created = self.api_core.create(Core.Class.CAMPAIGN_ONE_TO_ONE,
                                           entity_data,
                                           {Core.Message.MSG_NAME: message_name})
        except Core.CreateError as e:
            if 'new message' in e.message:
                message = ('None found: message_name=%s' % (message_name))
                raise Core.NoneFoundError(message)
            raise
        return self.api_core.store(Core.Class.CAMPAIGN_ONE_TO_ONE,
                                   {Core.Entity.ID: created})

    def send_to_list(self, message_name, list_name, scheduling_delay={Core.Scheduling.MINUTES: 3}):
        """
        Schedule the sending of an email campaign to a contact list.
        ------------------------------------------------
        @param message_name              - 'my_message'
        @param list_name                 - 'my_contact_list'
        @param [scheduling_delay]        - {Core.Scheduling.MINUTES: 3}
        @return result                   - storage result e.g. {beanName: bus_entity_campaign_delivery,
                                                                deliveryId: 7740786}
        """
        created = self.api_core.create(Core.Class.CAMPAIGN_DELIVERY)
        list_id = self.list_by_name(list_name,
                                    Core.Filters.key_filter(Core.List.ID))
        if list_id is None:
            message = ('None found: list_name=%s' % (list_name))
            raise Core.NoneFoundError(message)
        message_id = self.message_by_name(message_name,
                                          Core.Filters.key_filter(Core.Message.ID))
        if message_id is None:
            message = ('None found: message_name=%s' % (message_name))
            raise Core.NoneFoundError(message)

        utc_time = UTC_TIMEZONE.localize(
          datetime.datetime.utcnow() + datetime.timedelta(**scheduling_delay))
        schedule_time = utc_time.astimezone(GMT_TIMEZONE).strftime('%d/%m/%Y %H:%M')

        entity_data = {Core.Scheduling.DELIVERY_TIME: schedule_time,
                       Core.List.IDS: {'0': list_id},
                       Core.Message.ID: message_id,
                       Core.Entity.ID: created}
        return self.api_core.store(Core.Class.CAMPAIGN_DELIVERY, entity_data)


    def add_person(self, list_name, person, notify_uri=DEFAULT_NOTIFY_HTTP, strict_mode=True):
        """
        Proxy call to Helpers.add_people for a single person record
        ------------------------------------------------
        @param list_name                 - 'my_list_name'
        @param person                    - person dictionary with desired fields and values
        @param [notify_uri]              - email address to receive notification when finished
        @return result                   - storage result e.g. {beanName: bus_entity_campaign_list}
        """
        return self.add_people(list_name, [person], notify_uri, strict_mode)


    def add_people(self, list_name, people, notify_uri=DEFAULT_NOTIFY_HTTP, strict_mode=True):
        """
        Add multiple person records to a list
        ------------------------------------------------
        @param list_name                 - 'my_list_name'
        @param people                    - list of person dictionaries with desired fields and values
        @param [notify_uri]              - email address to receive notification when finished
                                           e.g. 'blackhole@example.com'
        @return result                   - storage result e.g. {beanName: bus_entity_campaign_list}
        """
        if list_name is None or list_name is '':
            message = ('Invalid list name: list_name=%s' % list_name)
            raise Core.InvalidListError(message)

        if strict_mode:
            strict_allowed_field_names = self.list_by_name(list_name, Core.Filters.key_filter(Core.List.CUSTOM_FIELDS))
            if strict_allowed_field_names is None:
                message = ('None found: list_name=%s' % list_name)
                raise Core.NoneFoundError(message)
        else:
            strict_allowed_field_names = None

        created = self.api_core.create(Core.Class.CAMPAIGN_LIST, {Core.Upload.TYPE: Core.Upload.APPEND})
        entity_data = {
          Core.List.NAME: list_name,
          Core.Upload.TYPE: Core.Upload.APPEND,
          Core.Upload.NOTIFY_URI: notify_uri,
          Core.Upload.NOTIFY_TYPE: NOTIFY_TYPE,
          Core.Entity.ID: created
        }
        paste_file = self.api_translator.encsv(people, strict_allowed_field_names)
        entity_data.update([self.api_translator.base_encode(Core.Upload.PASTE_FILE, paste_file)])
        entity_data.update(self.api_translator.csv_fields(paste_file))

        return self.api_core.store(Core.Class.CAMPAIGN_LIST, entity_data)

    def load_delivery(self, delivery_id):
        """
        Fetches delivery info
        """
        return self.api_core.load(Core.Class.CAMPAIGN_DELIVERY, {
          Core.Delivery.ID: delivery_id
        })

    def load_clicks(self):
        response = self.api_core.get_batch(Core.Class.EVENT_NOTIFICATION, {
          Core.Notification.TYPES: 'CLICK',
          Core.Notification.MAX: 1000,
          Core.Notification.MARK_AS_READ: 'N',
        })

        if response['resultData']['bus_entity_eventNotificationBatch']['eventData'] is None:
          return []

        csv_string = StringIO.StringIO(base64.b64decode(
          response['resultData']['bus_entity_eventNotificationBatch']['eventData']))
        csv.register_dialect(
          self.api_translator.CSV.DIALECT,
             escapechar=self.api_translator.CSV.ESCAPE,
             quotechar=self.api_translator.CSV.QUOTES,
             quoting=self.api_translator.CSV.QUOTING,
             skipinitialspace=self.api_translator.CSV.SKIP_INITIAL_SPACE)
        reader = csv.DictReader(
          csv_string,
          dialect=self.api_translator.CSV.DIALECT)
        reader.fieldnames = response['resultData']['bus_entity_eventNotificationBatch']['eventMeta']['CLICK'].split(',')
        return [line for line in reader]
