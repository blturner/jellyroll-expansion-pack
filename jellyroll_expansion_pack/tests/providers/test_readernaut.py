import json
import logging
import mock
import os

from django.test import TestCase

from jellyroll_expansion_pack.models import Book, BookProgress
from jellyroll_expansion_pack.providers import readernaut

f = open(os.path.join(
    os.path.dirname(__file__), 'fixtures/readernaut/response_1.json'))
json_file = f.read()
f.close()

mock_getjson = mock.Mock()
mock_getjson.return_value = json.loads(json_file)


class ReadernautProviderTestCase(TestCase):
    @mock.patch('jellyroll_expansion_pack.providers.readernaut.utils.getjson', mock_getjson)
    def setUp(self):
        readernaut.update()

    def test_enabled(self):
        self.assertEqual(readernaut.enabled(), True)

    @mock.patch('jellyroll_expansion_pack.providers.readernaut.utils.getjson', mock_getjson)
    def test_book_count_after_second_update(self):
        self.assertEqual(Book.objects.count(), 5)
        self.assertEqual(BookProgress.objects.count(), 10)

        book = Book.objects.get(title='Teenage Mutant Ninja Turtles')
        self.assertEqual(book.author, 'Kevin B. Eastman, Peter Laird')

        readernaut.update()
        self.assertEqual(Book.objects.count(), 5)

    @mock.patch('jellyroll_expansion_pack.providers.readernaut.utils.getjson', mock_getjson)
    @mock.patch('jellyroll_expansion_pack.providers.readernaut.log')
    def test_skips_updates(self, mock_log):
        readernaut.update()
        self.assertTrue(mock_log.info.called)

    @mock.patch('jellyroll_expansion_pack.providers.readernaut.utils.getjson', mock_getjson)
    @mock.patch('jellyroll_expansion_pack.providers.readernaut.log')
    def test_force_updates(self, mock_log):
        readernaut.update(force=True)
        self.assertFalse(mock_log.info.called)

