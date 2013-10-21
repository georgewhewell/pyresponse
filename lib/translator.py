#!/usr/bin/env python
# coding=utf-8
#

import base64
import StringIO
import csv

from core import Core

from suds import null as null

class Translator:

    class CSV:
        DIALECT = 'pyresponse-csv'

    main = None
    factory = None


    def __init__(self, main):
        self.main = main
        self.factory = main.api_client.factory


    def ensuds(self, dictionary):
        if not dictionary:
            return null()
        array = self.factory.create('paintArray')
        for key in dictionary:
            pair = self.factory.create('paintKeyValuePair')
            setattr(pair, 'key', self.x_encode(key, 'ignore'))
            value = getattr(pair, 'value')
            if isinstance(dictionary[key], dict):
                setattr(value, 'arr', self.ensuds(dictionary[key]))
            elif isinstance(dictionary[key], str) or isinstance(dictionary[key], unicode):
                escaped = self.x_encode(dictionary[key], 'xmlcharrefreplace')
                if isinstance(dictionary[key], unicode) and not key.isdigit() and not (key in self.main.unicode_exceptions):
                    escaped = base64.b64encode(escaped)
                    setattr(pair, 'key', getattr(pair, 'key') + '_base64')
                setattr(value, 'str', escaped)
            else:
                setattr(value, 'str', str(dictionary[key]))
            getattr(array, 'pairs').append(pair)
        return array


    def desuds(self, ptarr):
        dictionary = dict()
        if not hasattr(ptarr, 'pairs'):
            return None
        for pair in getattr(ptarr, 'pairs'):
            key = getattr(pair, 'key')
            value = getattr(pair, 'value')
            if key == 'result' and getattr(value, 'str') == 'success':
                dictionary['ok'] = True
            if hasattr(value, 'arr'):
                array = getattr(value, 'arr')
                if not array:
                    dictionary[key] = dict()
                else:
                    dictionary[key] = self.desuds(array)
            elif hasattr(value, 'str'):
                dictionary[key] = getattr(value, 'str')
        return dictionary


    def encsv(self, input_):
        if not isinstance(input_, list):
            input_ = [input_]

        master = set()
        for row in input_:
            master = master.union(row.keys())
        master = sorted(list(master))

        csv_string = StringIO.StringIO()
        csv.register_dialect(Translator.CSV.DIALECT,
                             escapechar='\\',
                             quotechar='"',
                             quoting=csv.QUOTE_MINIMAL,
                             skipinitialspace=True)

        csv_writer = csv.DictWriter(csv_string, master, dialect=Translator.CSV.DIALECT)

        csv_writer.writerow(dict([(k, k) for k in master]))

        for item in input_:
            csv_writer.writerow(dict([(k, self.x_encode(v).replace('\n', '')) for k, v in item.iteritems()]))

        output = csv_string.getvalue()
        csv_string.close()
        return output


    def response_data(self, dictionary, b_type=None, b_class=None, field='resultData'):
        try:
            if (b_type is not None) and (b_class is not None):
                if field is None:
                    return dictionary.get(b_type + '_' + b_class)
                return dictionary.get(field).get(b_type + '_' + b_class)
            elif (not b_type) and (not b_class):
                return dictionary.get(field)
            else:
                message = ('Mismatched parameter set, should be all or nothing: b_type=%s, b_class=%s' %
                           (b_type, b_class))
                raise Translator.ParameterError(message)
        except KeyError as e:
            message = 'KeyError caught. No such field exists: '
            if field in dictionary:
                message += ('field=%s' % (field))
            else:
                message += ('b_type=%s, b_class=%s --> %s' % (b_type, b_class, b_type + '_' + b_class))
            raise Translator.ParameterError(message)


    def response_stored(self, response, b_class):
        return self.response_data(response, Core.Type.ENTITY, b_class + '_key')

    def response_bean_id(self, response, b_class):
        return self.response_data(response, Core.Type.ENTITY, b_class).get(Core.Entity.ID)


    def response_found(self, response, b_class):
        return self.response_data(response, Core.Type.SEARCH, b_class).get(Core.Result.FOUND).values()


    def x_encode(self, string, errors='ignore'):
        if not (isinstance(string, str) or isinstance(string, unicode)):
            return str(string)
        if isinstance(string, str):
            string = string.decode('utf-8')
        return string.encode('ascii', errors)


    def base_encode(self, key, value):
        return (key + '_base64', base64.b64encode(value))


    def csv_fields(self, csv_string):
        entity_data = dict()
        count = 0
        custom = 0

        for key in csv_string.splitlines()[0].split(','):
            key_ = self.x_encode(key)
            if key_ == Core.Person.EMAIL or key_ == Core.Person.MOBILE:
                entity_data[key_ + 'Col'] = count
            else:
                field = 'field' + str(count + 1)
                entity_data[field + 'Col'] = count
                entity_data[field + 'Name'] = key.replace(' ', '_')
                custom += 1
                if custom > self.main.api_account_level:
                    message = ('Above account limit: api_account_level=%s (custom fields available)' %
                               (self.main.api_account_level))
                    raise AccountLevelError(message)
            count += 1
        return entity_data


    def null(self):
        return null()


    class ParameterError(Exception):
        pass

    class AccountLevelError(Exception):
        pass

