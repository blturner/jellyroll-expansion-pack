import json
import mock
import os
import responses
import pytz

from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from jellyroll.models import Item

from jellyroll_expansion_pack.models import Tweet
from jellyroll_expansion_pack.providers import twitter

utc = pytz.utc

f = open(os.path.join(
    os.path.dirname(__file__), 'fixtures/twitter.json'))
twitter_json = f.read()
f.close()

loaded_json = json.loads(twitter_json)


class TwitterProviderTests(TestCase):
    @responses.activate
    def setUp(self):
        responses.add(
            responses.POST,
            'https://api.twitter.com/oauth2/token',
            status=200,
            body='{"token_type":"bearer","access_token":"AAAA%2FAAA%3DAAAAAAAA"}')

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/user_timeline.json?count=200&screen_name=blturner',
            match_querystring=True,
            status=200,
            body=twitter_json,
            content_type='application/json')

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/user_timeline.json?count=200&max_id=239413543487819778&screen_name=blturner',
            match_querystring=True,
            status=404,
            body='{"errors": {"message": "Sorry, that page does not exist", "code": 34}}',
            content_type='application/json')

        twitter.update()

    @mock.patch('jellyroll_expansion_pack.providers.twitter.log')
    def test_skips_updates(self, mock_log):
        twitter.update()
        self.assertTrue(mock_log.info.called)

    def test_jellyroll_items_added(self):
        items = Item.objects.filter(content_type__model='tweet')
        self.assertEqual(items.count(), 2)

        self.assertEqual(items[0].object_str, loaded_json[0]['text'])
        self.assertEqual(items[0].timestamp, datetime(2012,8,29,17,12,58,tzinfo=utc))

        self.assertEqual(items[1].object_str, loaded_json[1]['text'])
        self.assertEqual(items[1].timestamp, datetime(2012,8,25,17,26,51,tzinfo=utc))

    def test_tweet_model(self):
        tweets = Tweet.objects.all()

        self.assertEqual(Tweet.objects.count(), 2)
        self.assertEqual(tweets[0].created_at, datetime(2012,8,29,17,12,58,tzinfo=utc))
        self.assertEqual(tweets[0].id_str, loaded_json[0]['id_str'])
        self.assertEqual(tweets[0].text, loaded_json[0]['text'])
        self.assertEqual(tweets[0].tweet_id, loaded_json[0]['id'])

        self.assertEqual(tweets[1].created_at, datetime(2012,8,25,17,26,51,tzinfo=utc))
        self.assertEqual(tweets[1].id_str, loaded_json[1]['id_str'])
        self.assertEqual(tweets[1].text, loaded_json[1]['text'])
        self.assertEqual(tweets[1].tweet_id, loaded_json[1]['id'])

