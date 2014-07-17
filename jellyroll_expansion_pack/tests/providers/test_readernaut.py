import json
import logging
import mock
import os

from django.test import TestCase

from jellyroll_expansion_pack.models import Book
from jellyroll_expansion_pack.providers import readernaut

json_file = open(os.path.join(
    os.path.dirname(__file__), 'fixtures/readernaut/response_1.json'))

mock_getjson = mock.Mock()
mock_getjson.return_value = json.load(json_file)


class ReadernautProviderTestCase(TestCase):
    @mock.patch('jellyroll.providers.utils.getjson', mock_getjson)
    def setUp(self):
        readernaut.update()

    def test_enabled(self):
        self.assertEqual(readernaut.enabled(), True)

    @mock.patch('jellyroll.providers.utils.getjson', mock_getjson)
    def test_book_count_after_second_update(self):
        self.assertEqual(Book.objects.all().count(), 5)

        readernaut.update()
        self.assertEqual(Book.objects.all().count(), 5)

    def test_multiple_authors(self):
        book = Book.objects.get(title='Teenage Mutant Ninja Turtles')
        self.assertEqual(book.author, 'Kevin B. Eastman, Peter Laird')

    @mock.patch('jellyroll_expansion_pack.providers.readernaut.log')
    def test_skips_updates(self, mock_log):
        readernaut.update()
        self.assertTrue(mock_log.info.called)

    @mock.patch('jellyroll_expansion_pack.providers.readernaut.log')
    def test_force_updates(self, mock_log):
        readernaut.update(force=True)
        self.assertFalse(mock_log.info.called)

