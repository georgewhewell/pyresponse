pyresponse
==========
**PureResponseClient**  
Python API wrapper for PureResponse PAINT

**MIT License**  
Copyright (c) 2013 Mikael Kohlmyr, Triggered Messaging Ltd  
mikael.kohlmyr@triggeredmessaging.com

[Triggered Messaging](http://www.triggeredmessaging.com),   
[Pure360](http://www.pure360.com)

API Examples  
==========
**Import**  
```python
from pyresponse import PureResponseClient as PureResponseClient
```
==========
**Initialise**  
```python
pureresponse = PureResponseClient()
```
==========
**Authenticate**  
```python
pureresponse.authenticate('username', 'password')
```
==========
**Create list**  
```python
# with single record
pureresponse.create_list('new_list_name', 
                         {'email': 'blackhole@example.com', 'name': 'John Doe'})
# with multiple records
pureresponse.create_list('new_list_name', 
                         [{'email': 'mars@example.com', 'name': 'John Doe'}, 
                          {'email': 'venus@example.com', 'name': 'Jane Doe'}])
```
==========
**Append list**  
```python
# single record
pureresponse.add_person('new_list_name', 
                        {'email': 'blackhole@example.com', 
                         'name': 'John Doe'})
# multiple records
pureresponse.add_person('new_list_name', 
                        [{'email': 'mars@example.com', 'name': 'John Doe'}, 
                         {'email': 'venus@example.com', 'name': 'Jane Doe'}])
```
==========
**Create message**  
```python
pureresponse.create_message('new_message_name', 
                            'subject line', 
                            '<h1>Headline</h1><p>body of text</p>')
```
==========
**Send single message**  
```python
pureresponse.send_to_person('new_message_name', 'recipient@example.com')
```
==========
**Send campaign message**  
```python
pureresponse.send_to_list('new_message_name', 'new_list_name')
```
==========
**Get person**  
```python
# by email address
pureresponse.person_by_email('blackhole@example.com')
# by person id
pureresponse.person_by_id('555555555')
```
==========
**Get list**  
```python
# by list name
pureresponse.list_by_name('new_list_name')
# by list id
pureresponse.list_by_id('555555')
```
==========
**Get message**  
```python
# by message name
pureresponse.message_by_name('new_message_name')
# by message id
pureresponse.message_by_id('555555')
```
For more readily available api calls, see [helpers.py](lib/helpers.py)  

==========
**Using constants**  
```python
# e.g.
>>> pureresponse.Message.ID
'messageId'
>>> pureresponse.Upload.TYPE
'uploadTransactionType'
# for more constants see ./lib/core.py
```
==========
**Using core methods**  
```python
# e.g.
# replicating behaviour of pureresponse.person_by_id('555555555')
pureresponse.api_core.load(pureresponse.Class.CAMPAIGN_PERSON, 
                           {pureresponse.Person.ID: '555555555'})
# replicating behaviour of pureresponse.person_by_email('blackhole@example.com')
search_params = {pureresponse.Person.EMAIL: 'blackhole@example.com'}
loaded = pureresponse.api_core.load_search(pureresponse.Class.CAMPAIGN_PERSON, 
                                           search_params)
person = pureresponse.api_core.filter_loaded(loaded, search_params, None)
result = person[0] if len(person) else None
# both methods will return the same structure (a person record)
```
==========
**Putting calls together**  
```python
# in this call we use an output filter on pureresponse.list_by_name, 
# instead of returning a list record, it will return a list id
key_filter = pureresponse.Filters.key_filter(pureresponse.List.ID)
my_list_id = pureresponse.list_by_name('my_list_name', 
                                       output_filter=key_filter)
# again we are using an output filter, this time we output only 
# the set of filter names rather than the set of full filter records
key_filter = pureresponse.Filters.key_filter(pureresponse.Filter.NAME)
list_filter_names = pureresponse.filters_for_list_id(my_list_id, 
                                                     output_filter=key_filter)
```
==========
**Output filters**  
An output filter is a closure where the inner function will operate on a dictionary "candidate" and return some subset of the information within
```python
# e.g.
# reimplementing pureresopnse.Filters.key_filter
# only returns the value of the field (key) being filtered on
def key_filter(key):
    def closed(candidate):
        return candidate.get(key)
    return closed
```

API Concepts and Internals  
==========
**PureResponse Application Interface (PAINT)**  
PAINT is an interface to PureResponse which is accessed through the [Simple Object Access Protocol](http://en.wikipedia.org/wiki/SOAP).  
However, unlike in a traditional SOAP implementation, all calls are made to the same handler which then dispatches calls internally to PureResponse. This means different calls are distinguished based on parameters which specify what data to operate on and how to operate on it, e.g. `bus_facade_campaign_list` and `create`.  

```python
context = self.api_context or self.api_translator.null()
bean = bean_type + '_' + bean_class
entity_data = self.api_translator.ensuds(entity_data)
process_data = self.api_translate.ensuds(process_data)
response = self.api_client.service.handleRequest(context,
                                                 bean,
                                                 bean_proc,
                                                 entity_data,
                                                 process_data)
result = self.api_translator.desuds(response)
```
==========
**Beans**  
The term `bean` is used in PureResponse to refer to logical entities that contain or manage data, not unlike objects.  

| Bean type | Prefix       | Description                                                       |
| --------- | ------------ | ----------------------------------------------------------------- |
| Entity    | `bus_entity` | The representations of the core data in PureResponse.             |
| Facade    | `bus_facade` | Proxies for accessing and manipulating Entity and Search beans.   |
| Search    | `bus_search` | Define how entities are searchable and format results.            |

In essence all calls are made to a `bus_facade` beans and from there `bus_entity` and `bus_search` beans are used or manipulated.
