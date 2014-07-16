import json
import mock
import os

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import is_aware

from jellyroll.models import Item
from jellyroll_expansion_pack.providers import dribbble

json_file = open(os.path.join(
    os.path.dirname(__file__), 'fixtures/dribbble/shots.json'))

mock_getjson = mock.Mock()
mock_getjson.return_value = json.load(json_file)


class DribbbleProviderTests(TestCase):
    def test_enabled(self):
        self.assertEqual(dribbble.enabled(), True)

    @mock.patch('jellyroll.providers.utils.getjson', mock_getjson)
    def test_update(self):
        dribbble.update()
        items = Item.objects.filter(content_type__model='shot').order_by('-timestamp')
        self.assertEqual(len(items), 3)
        if settings.USE_TZ:
          self.assertTrue(is_aware(items[0].timestamp))
