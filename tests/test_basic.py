import uuid
from unittest import TestCase

from pyresponse import PureResponseClient as PureResponseClient

ListName = lambda: str(uuid.uuid4())


class BasicTests(TestCase):
    
    def setUp(self):
        self.client = PureResponseClient()
        self.client.authenticate('tm.system', 'crwkbplf')

    def test_create_list(self):
        self.client.create_list(ListName(), 
            {'email': 'blackhole@example.com', 'name': 'John Doe'})

    def test_create_list_multiple(self):
        self.client.create_list(ListName(), 
            [{'email': 'mars@example.com', 'name': 'John Doe'}, {'email': 'venus@example.com', 'name': 'Jane Doe'}])
