pyresponse
==========
**PureResponseClient**  
Python API wrapper for PureResponse PAINT

**MIT License**  
Copyright (c) 2013 Mikael Kohlmyr, Triggered Messaging Ltd  
mikael.kohlmyr@triggeredmessaging.com

[Triggered Messaging](http://www.triggeredmessaging.com),   
[Pure360](http://www.pure360.com)

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
pureresponse.create_list('new_list_name', {'email': 'blackhole@example.com', 'name': 'John Doe'})
# with multiple records
pureresponse.create_list('new_list_name', [{'email': 'mars@example.com', 'name': 'John Doe'}, {'email': 'venus@example.com', 'name': 'Jane Doe'}])
```
==========
**Append list**  
```python
# single record
pureresponse.add_person('new_list_name', {'email': 'blackhole@example.com', 'name': 'John Doe'})
# multiple records
pureresponse.add_person('new_list_name', [{'email': 'mars@example.com', 'name': 'John Doe'}, {'email': 'venus@example.com', 'name': 'Jane Doe'}])
```
==========
**Create message**  
```python
pureresponse.create_message('new_message_name', 'subject line', '<h1>Headline</h1><p>body of text</p>')
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
