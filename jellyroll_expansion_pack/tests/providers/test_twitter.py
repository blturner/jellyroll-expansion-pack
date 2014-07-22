import json
import mock

from django.conf import settings
from django.test import TestCase

from jellyroll_expansion_pack.providers import twitter

class MockResponse(object):
    content = '[]'

mock_response = MockResponse()

mock_requests_get = mock.Mock()
mock_requests_get.return_value = mock_response


class TwitterProviderTests(TestCase):
    @mock.patch('requests.get', mock_requests_get)
    def test_update(self):
        twitter.update()
