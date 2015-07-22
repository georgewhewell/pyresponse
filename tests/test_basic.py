import uuid
import pytest

from unittest import TestCase

from pyresponse import PureResponseClient as PureResponseClient

# Generate a random string to name things
Name = lambda: str(uuid.uuid4())


class BasicTests(TestCase):
    
    def setUp(self):
        self.client = PureResponseClient()
        self.client.authenticate('tm.system', 'crwkbplf')

    @pytest.mark.xfail  # Cannot create list with empty recipients
    def test_create_empty_list(self):
        self.client.create_list(Name(), [])    
    
    def test_create_list(self):
        self.client.create_list(Name(), 
            {'email': 'blackhole@example.com', 'name': 'John Doe'})

    def test_create_list_multiple(self):
        self.client.create_list(Name(), [{
            'email': 'mars@example.com', 'name': 'John Doe'},
            {'email': 'venus@example.com', 'name': 'Jane Doe'}
        ])
            
    def test_add_person_to_list(self):
        list_name = Name()
        self.client.create_list(list_name, [
            {'email': 'blackhole1@example.com', 'name': 'John Doe 1'}])
        self.client.wait_for_list(list_name)
        self.client.add_person(list_name,
            {'email': 'blackhole@example.com', 'name': 'John Doe'})

    def test_add_people_to_list(self):
        list_name = Name()
        self.client.create_list(list_name, [
            {'email': 'blackhole1@example.com', 'name': 'John Doe 1'}])
        self.client.wait_for_list(list_name)
        self.client.add_people(list_name, [
            {'email': 'mars@example.com', 'name': 'John Doe'}, 
            {'email': 'venus@example.com', 'name': 'Jane Doe'}
        ])

    def test_create_message(self):
        self.client.create_message(
            Name(),
            'subject line',
            '<h1>Headline</h1><p>body of text</p>'
        )

    def test_single_message(self):
        message_name = Name()
        self.client.create_message(
            message_name,
            'subject line',
            '<h1>Headline</h1><p>body of text</p>'
        )
        self.client.send_to_person(
            message_name, 'recipient@example.com')

    def test_send_campaign_message(self):
        message_name = Name()
        list_name = Name()
        self.client.create_message(
            message_name,
            'subject line',
            '<h1>Headline</h1><p>body of text</p>'
        )
        self.client.create_list(list_name, [{
            'email': 'mars@example.com', 'name': 'John Doe'},
            {'email': 'venus@example.com', 'name': 'Jane Doe'}
        ])
        self.client.wait_for_list(list_name)
        self.client.send_to_list(message_name, list_name)

    def test_get_person(self):
        self.client.person_by_email('blackhole@example.com')

    def test_get_list(self):
        list_name = Name()
        self.client.create_list(list_name, [{'email': 'venus@example.com', 'name': 'Jane Doe'}])
        self.client.wait_for_list(list_name)
        self.client.list_by_name(list_name)
