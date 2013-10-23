
import random
import string

from pyresponse import PureResponseClient as PureResponseClient

def rand_email():
    return rand_name(6).lower() + str(random.randint(100,999)) + '@example.com'

def rand_name(N):
    return ''.join(random.choice(string.ascii_lowercase) for x in range(N)).capitalize()

def rand_person():
    return {'email' : rand_email(), 'name': rand_name(5) + ' ' + rand_name(7)}

def rand_set_of_x(factory):
    return [factory() for x in range(3, random.randint(5,12))]


api = PureResponseClient()

print '------------------------------------------------'
print 'Authenticate'
try:
    print api.authenticate('tm.system', 'crwkbplf')
except Exception as e:
    print e
print '------------------------------------------------'
print 'Create list with single person'
try:
    print api.create_list('new_list_name_a', rand_person(), rand_email(), True)
except Exception as e:
    print e
print '------------------------------------------------'
##
## Note that the following calls are commented out as they
## will fail since Pure 360 can't process requests fast enough
## "already pending in queue"
##
# print 'Create list with many people'
# try:
#     print api.create_list('new_list_name_b', rand_set_of_x(rand_person), rand_email(), True)
# except Exception as e:
#     print e
# print '------------------------------------------------'
# print 'Add person to list'
# try:
#     print api.add_person('new_list_name_a', rand_person(), rand_email())
# except Exception as e:
#     print e
# print '------------------------------------------------'
# print 'Add people to list'
# try:
#     print api.add_people('new_list_name_b', rand_set_of_x(rand_person), rand_email())
# except Exception as e:
#     print e
# print '------------------------------------------------'
print 'Create message'
try:
    print api.create_message('new_message_name', 'subject line', '<h1>Headline</h1><p>body of text</p>', rand_email())
except Exception as e:
    print e
print '------------------------------------------------'
print 'Send single message'
try:
    print api.send_to_person('new_message_name', rand_email())
except Exception as e:
    print e
print '------------------------------------------------'
print 'Send campaign message'
try:
    print api.send_to_list('new_message_name', 'new_list_name_a')
except Exception as e:
    print e.message
print '------------------------------------------------'
