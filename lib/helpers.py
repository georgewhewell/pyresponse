#!/usr/bin/env python
# coding=utf-8
#

from core import Core

import datetime

class Helpers:

    def person_by_email(self, email_address, output_filter=None):
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_PERSON,
                                           {Core.Person.EMAIL: email_address})
        person = self.api_core.filter_loaded(loaded,
                                             {Core.Person.EMAIL: email_address},
                                             output_filter)
        return person[0] if len(person) else None


    def person_by_id(self, person_id):
        return self.api_core.load(Core.Class.CAMPAIGN_PERSON,
                                  {Core.Person.ID: person_id})


    def list_by_name(self, list_name, output_filter=None):
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_LIST,
                                           {Core.List.NAME: list_name})
        list_ = self.api_core.filter_loaded(loaded,
                                            {Core.List.NAME: list_name},
                                            output_filter)
        return list_[0] if len(list_) else None


    def list_by_id(self, list_id):
        return self.api_core.load(Core.Class.CAMPAIGN_LIST,
                                  {Core.List.ID: list_id})


    def message_by_name(self, message_name, output_filter=None):
        loaded = self.api_core.load_search(Core.Class.CAMPAIGN_EMAIL,
                                           {Core.Message.NAME: message_name})
        message = self.api_core.filter_loaded(loaded,
                                              {Core.Message.NAME: message_name},
                                              output_filter)
        return message[0] if len(message) else None

    def message_by_id(self, message_id):
        return self.api_core.load(Core.Class.CAMPAIGN_EMAIL,
                                  {Core.Message.ID: message_id})

    def create_message(self, message_name, subject, message_body, overwrite_existing=False):
        self.api_core.handle_existing(Core.Class.CAMPAIGN_EMAIL,
                                      self.message_by_name(message_name),
                                      overwrite_existing)
        created = self.api_core.create(Core.Class.CAMPAIGN_EMAIL)
        entity_data = {Core.Message.NAME: message_name,
                       Core.Message.SUBJECT: subject,
                       Core.Message.BODY_HTML: message_body,
                       Core.Entity.ID: created}
        return self.api_core.store(Core.Class.CAMPAIGN_EMAIL, entity_data)


    def create_list(self, list_name, list_data, notify_uri=None, overwrite_existing=False):
        self.api_core.handle_existing(Core.Class.CAMPAIGN_LIST,
                                      self.list_by_name(list_name),
                                      overwrite_existing)

        created = self.api_core.create(Core.Class.CAMPAIGN_LIST)
        paste_file = self.api_translator.encsv(list_data)

        entity_data = dict(list({Core.Upload.NOTIFY_URI: notify_uri,
                                 Core.List.NAME: list_name,
                                 Core.Entity.ID: created,
                                 Core.Upload.PASTE_FILE: paste_file}.items()) +
                                          [self.api_translator.csv_fields(paste_file)])
        return self.api_core.store(Core.Class.CAMPAIGN_LIST, entity_data)


    def send_to_person(self, message_name, email_address, custom_data=None):
        entity_data = {Core.Message.TO_ADDRESS: email_address}
        if custom_data is not None:
            entity_data[Core.Message.CUSTOM_DATA] = custom_data
        created = self.api_core.create(Core.Class.CAMPAIGN_ONE_TO_ONE,
                                       entity_data,
                                       {Core.Message.MSG_NAME: message_name})
        return self.api_core.store(Core.Class.CAMPAIGN_ONE_TO_ONE,
                                   {Core.Entity.ID: created})


    def send_to_list(self, message_name, list_name, scheduling_delay = {Core.Scheduling.MINUTES: 3}):
        created = self.api_core.create(Core.Class.CAMPAIGN_DELIVERY)
        list_id = self.list_by_name(list_name,
                                    Core.Filters.key_filter(Core.List.ID))
        if list_id is None:
            message = ('None found: list_name=%s' % (list_name))
            raise Helpers.NoneFoundError(message)
        message_id = self.message_by_name(message_name,
                                          Core.Filters.key_filter(Core.Message.ID))
        if message_id is None:
            message_id = ('None found: message_name=%s' % (message_name))
            raise Helpers.NoneFoundError(message)
        schedule_time = datetime.datetime.now() + datetime.timedelta(**scheduling_delay)
        schedule_time = schedule_time.strftime('%d/%m/%Y %H:%M')

        entity_data = {Core.Scheduling.DELIVERY_TIME: schedule_time,
                       Core.List.IDS: {'0': list_id},
                       Core.Message.ID: message_id,
                       Core.Entity.ID: created}
        return self.api_core.store(Core.Class.CAMPAIGN_DELIVERY, entity_data)


    def add_person(self, list_name, person, notify_uri=None):
        return self.add_people(list_name, [person], notify_uri)


    def add_people(self, list_name, people, notify_uri=None):
        # structure more like create_list which does most of the same stuff
        entity_data = {Core.List.NAME: list_name,
                       Core.Upload.TYPE: 'APPEND',
                       Core.Upload.NOTIFY_URI: notify_uri}
        paste_file = self.api_translator.encsv(people)
        entity_data.update([self.api_translator.base_encode(Core.Upload.PASTE_FILE,
                                                            paste_file)])
        entity_data.update(self.api_translator.csv_fields(paste_file))
        created = self.api_core.create(Core.Class.CAMPAIGN_LIST)
        entity_data.update({Core.Entity.ID: created})
        return self.api_core.store(Core.Class.CAMPAIGN_LIST, entity_data)


    class NoneFoundError(Exception):
        pass
