import json
import mock
import os
import responses
import pytz

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from jellyroll.models import Item
from social.apps.django_app.default.models import UserSocialAuth

from jellyroll_expansion_pack.models import Tweet
from jellyroll_expansion_pack.providers import twitter

utc = pytz.utc

f = open(os.path.join(
    os.path.dirname(__file__), 'fixtures/twitter.json'))
twitter_json = f.read()
f.close()

f = open(os.path.join(
    os.path.dirname(__file__), 'fixtures/resp.json'))
since_id_json = f.read()
f.close()

loaded_json = json.loads(twitter_json)


def add_responses():
    responses.add(
        responses.POST, 'https://api.twitter.com/oauth2/token',
        status=200,
        body='{"token_type":"bearer","access_token":"access_token"}',
        content_type='application/json')

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
        status=200,
        body=since_id_json,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://api.twitter.com/1.1/statuses/user_timeline.json?count=200&max_id=1&screen_name=blturner',
        match_querystring=True,
        status=200,
        body='[]',
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://api.twitter.com/1.1/statuses/user_timeline.json?count=200&screen_name=blturner&since_id=1',
        match_querystring=True,
        status=200,
        body='[]',
        content_type='application/json')


class TwitterProviderTests(TestCase):
    def setUp(self):
        user = User(username='bturner')
        user.save()

        social_auth = UserSocialAuth(
            uid='123',
            user=user,
            provider='twitter')
        social_auth.save()

    def tearDown(self):
        User.objects.all().delete()
        UserSocialAuth.objects.all().delete()

    @responses.activate
    @mock.patch('jellyroll_expansion_pack.providers.twitter.log')
    def test_skips_updates(self, mock_log):
        add_responses()

        twitter.update()
        self.assertEqual(Item.objects.count(), 3)

        twitter.update()
        self.assertTrue(mock_log.info.called)
        self.assertEqual(Item.objects.count(), 3)

    @responses.activate
    def test_twitter_client(self):
        responses.add(
            responses.POST, 'https://api.twitter.com/oauth2/token',
            status=200,
            body='{"token_type":"bearer","access_token":"access_token"}',
            content_type='application/json')

        social_auth = UserSocialAuth.objects.all()[0]
        self.assertEqual(social_auth.extra_data, {})

        c = twitter.TwitterClient(social_auth, 'twitter_username')
        self.assertEqual(
            c.get_api_token(),
            {u'token_type': u'bearer', u'access_token': u'access_token'}
        )

    @responses.activate
    def test_jellyroll_items_added(self):
        add_responses()
        twitter.update()

        items = Item.objects.filter(content_type__model='tweet')

        self.assertEqual(items.count(), 3)
        self.assertEqual(Tweet.objects.count(), 3)

        item = items[0]
        tweet = Tweet.objects.get(id=item.object.id)

        self.assertEqual(item.object_str, tweet.text)
        self.assertEqual(item.timestamp, tweet.created_at)

        item = items[1]
        tweet = Tweet.objects.get(id=item.object.id)

        self.assertEqual(item.object_str, tweet.text)
        self.assertEqual(item.timestamp, tweet.created_at)

    @responses.activate
    def test_tweet_model(self):
        add_responses()
        twitter.update()

        tweets = Tweet.objects.all()

        self.assertEqual(Tweet.objects.count(), 3)

        self.assertEqual(tweets[0].text, 'A new tweet')

        self.assertEqual(tweets[1].created_at, datetime(2012,8,29,17,12,58,tzinfo=utc))
        self.assertEqual(tweets[1].id_str, loaded_json[0]['id_str'])
        self.assertEqual(tweets[1].profile_image_url, loaded_json[0]['user']['profile_image_url'])
        self.assertEqual(tweets[1].text, loaded_json[0]['text'])
        self.assertEqual(tweets[1].tweet_id, loaded_json[0]['id'])
        self.assertEqual(tweets[1].user_id_str, int(loaded_json[0]['user']['id_str']))
        self.assertEqual(tweets[1].username, loaded_json[0]['user']['name'])

        self.assertEqual(tweets[2].created_at, datetime(2012,8,25,17,26,51,tzinfo=utc))
        self.assertEqual(tweets[2].id_str, loaded_json[1]['id_str'])
        self.assertEqual(tweets[2].profile_image_url, loaded_json[1]['user']['profile_image_url'])
        self.assertEqual(tweets[2].text, loaded_json[1]['text'])
        self.assertEqual(tweets[2].tweet_id, loaded_json[1]['id'])
        self.assertEqual(tweets[2].user_id_str, int(loaded_json[1]['user']['id_str']))
        self.assertEqual(tweets[2].username, loaded_json[1]['user']['name'])
