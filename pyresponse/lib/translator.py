#!/usr/bin/env python
# coding=utf-8
#

import base64
import StringIO
import csv
import re

from suds import null as null

from .core import Core


class Translator:

    class CSV:
        DIALECT = 'pyresponse-csv'
        QUOTES = '"'
        ESCAPE = '\\'
        QUOTING = csv.QUOTE_MINIMAL
        SKIP_INITIAL_SPACE = True

    main = None
    factory = None


    def __init__(self, main):
        self.main = main
        self.factory = main.api_client.factory


    def ensuds(self, dictionary):
        """
        Turn a dictionary into a soap structure as defined by the wsdl
        from pyresponse.Api used when instantiating the API wrapper.
        Dictionaries become paintArrays, key, value pairs from the
        dictionary become paintKeyValuePair objects.

        Also manages encoding of keys and values.
        ------------------------------------------------
        @param dictionary                - dictionary of request data
        @return result                   - soap representation of that same data
        """
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
                if isinstance(dictionary[key], unicode) and not key.isdigit() and not (key in self.main.encoding_exceptions):
                    (key, escaped) = self.base_encode(getattr(pair, 'key'), escaped)
                    setattr(pair, 'key', key)

                setattr(value, 'str', escaped)
            else:
                setattr(value, 'str', str(dictionary[key]))
            getattr(array, 'pairs').append(pair)
        return array


    def desuds(self, ptarr):
        """
        Turn a soap structure (response) into a dictionary.
        Make dictionaries from paintArrays, paintKeyValuePairs become
        keys and values.
        ------------------------------------------------
        @param ptarr                     - soap datastructure
        @return result                   - dictionary representation of that same data
        """
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


    def encsv(self, input_, strict_allowed_field_names=None):
        """
        Turn dictionary or list of dictionaries into a csv string.
        Create a master list of keys in the dictionaries, from the
        master list establish the top row of the csv field.
        Then fill it out with values from each dictionary using a
        DictWriter.
        ------------------------------------------------
        @param input_                    - (shallow) dictionary or list of dictionaries
        @return result                   - csv string representing that same data, adhering
                                           to the csv dialect defined by the properties of
                                           Translator.CSV
        """
        if not isinstance(input_, list):
            input_ = [input_]

        master = set()
        for row in input_:
            if not row or not any(row):
                message = ('Invalid person record(s): empty record person=%s in people=%s' % (row, input_))
                raise Core.InvalidPersonError(message)
            try:
                master = master.union(row.keys())
            except AttributeError as e:
                message = ('Invalid person record(s): person=%s in people=%s' % (row, input_))
                raise Core.InvalidPersonError(message)
        master = sorted(list(master))

        if strict_allowed_field_names is not None:
            for item in master:
                if (self.x_encode(item) in [Core.Person.EMAIL, Core.Person.MOBILE]):
                    continue
                if item not in strict_allowed_field_names:
                    message = ('Invalid person record(s): not in set of allowed fields field_name=%s (strict_mode)' % (item))
                    raise Core.InvalidPersonError(message)

        csv_string = StringIO.StringIO()
        csv.register_dialect(Translator.CSV.DIALECT,
                             escapechar=Translator.CSV.ESCAPE,
                             quotechar=Translator.CSV.QUOTES,
                             quoting=Translator.CSV.QUOTING,
                             skipinitialspace=Translator.CSV.SKIP_INITIAL_SPACE)

        csv_writer = csv.DictWriter(csv_string, master, dialect=Translator.CSV.DIALECT)

        csv_writer.writerow(dict([(k, k) for k in master]))

        for item in input_:
            csv_writer.writerow(dict([(k, self.x_encode(v).replace('\n', '')) for k, v in item.iteritems()]))

        output = csv_string.getvalue()
        csv_string.close()
        return output


    def response_data(self, dictionary, b_type=None, b_class=None, field='resultData'):
        """
        From a multi-level dictionary, grab the fields that
        contain the relevant information for the call that was made.
        ------------------------------------------------
        @param dictionary                - e.g. {'resultData' : {'bus_facade_campaign_list' : {..}}}
        @param [b_type]                  - any property of Core.Type, e.g. bus_facade
        @param [b_class]                 - any property of Core.Class, e.g. campaign_list
        @param [field]                   - result field, defaults to resultData
        @return result                   - given example parameters: {..}
        """
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
                raise Core.ParameterError(message)
        except KeyError as e:
            message = 'KeyError caught. No such field exists: '
            if field in dictionary:
                message += ('field=%s' % (field))
            else:
                message += ('b_type=%s, b_class=%s --> %s' % (b_type, b_class, b_type + '_' + b_class))
            raise Core.ParameterError(message)


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

    def htmldecode(self, string):
        """
        Fredrik Lundh,
        http://effbot.org/zone/re-sub.htm#unescape-html
        """
        def replace(match):
            text = match.group(0)
            if text[:2] == "&#":
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text
        return re.sub("&#?\w+;", replace, string)


    def base_encode(self, key, value):
        return (key + '_base64', base64.b64encode(value))


    def csv_fields(self, csv_string):
        """
        Split the heading row and build a dictionary which
        indexes them in accordance with the PureResponse
        specification. Custom fields are numbered, email
        and mobile fields are attached to standard fields
        through a similar naming convention.

        Going above pre-defined account limits will raise
        an exception.
        ------------------------------------------------
        @param csv_string                - email, my_custom_field
        @return result                   - {'emailCol': 0, field2Col: 1,
                                            'field2Name': 'my_custom_field'}
        """
        entity_data = dict()
        count = 0
        custom = 0

        for key in csv_string.splitlines()[0].split(','):
            key_ = self.x_encode(key)
            if key_ in [Core.Person.EMAIL, Core.Person.MOBILE]:
                entity_data[key_ + 'Col'] = count
            else:
                field = 'field' + str(count + 1)
                entity_data[field + 'Col'] = count
                entity_data[field + 'Name'] = key.replace(' ', '_')
                custom += 1
                if custom > self.main.api_account_level:
                    message = ('Above account limit: api_account_level=%s (custom fields available)' %
                               (self.main.api_account_level))
                    raise Core.AccountLevelError(message)
            count += 1
        return entity_data


    def null(self):
        return null()
