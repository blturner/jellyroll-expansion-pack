import base64
import dateutil
import json
import logging
import requests
import urllib

from dateutil.parser import parse

from django.conf import settings

from jellyroll.models import Item
from social.apps.django_app.default.models import UserSocialAuth

from jellyroll_expansion_pack.models import Tweet


log = logging.getLogger('jellyroll_expansion_pack.providers.twitter')


class TwitterClient(object):
    def __init__(self, social_auth, username, method="1.1"):
        self.social_auth = social_auth
        self.username = username
        self.method = method

        self.get_api_token()

    def get(self, path, **kwargs):
        headers = {
            'authorization': '{0} {1}'.format(
                self.social_auth.extra_data['basic']['token_type'],
                self.social_auth.extra_data['basic']['access_token'])
        }

        kwargs['screen_name'] = self.username

        url = '/'.join((
            'https://api.twitter.com',
            self.method,
            path + '.json?')) + urllib.urlencode(kwargs)
        return requests.get(url, headers=headers)

    def get_api_token(self):
        try:
            return self.social_auth.extra_data['basic']
        except KeyError:
            self.set_api_token()

    def set_api_token(self):
        token = '{0}:{1}'.format(settings.TWITTER_API_KEY,
                                 settings.TWITTER_API_SECRET)
        headers = {
            'authorization': 'Basic {0}'.format(base64.b64encode(token)),
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        response = requests.post('https://api.twitter.com/oauth2/token',
                                 headers=headers,
                                 data='grant_type=client_credentials')
        api_token = json.loads(response.content)

        social_auth = self.social_auth
        social_auth.extra_data['basic'] = {}
        social_auth.extra_data['basic']['token_type'] = api_token['token_type']
        social_auth.extra_data['basic']['access_token'] = api_token['access_token']
        social_auth.save()


def enabled():
    return True


def update():
    client = since_id = None
    kwargs = {}
    last_update_date = Item.objects.get_last_update_of_model(Tweet)
    tweet_items = Item.objects.get_for_model(Tweet)

    for social_auth in UserSocialAuth.objects.filter(provider='twitter'):
        client = TwitterClient(social_auth, settings.TWITTER_USERNAME)

    if tweet_items:
        kwargs['since_id'] = Tweet.objects.get(
            id=tweet_items[0].object_id).tweet_id

    if not client:
        log.info('No SocialAuth objects were found to process.')
        return

    _handle_tweets(client, last_update_date, **kwargs)


def _handle_tweets(client, last_update_date=None, **kwargs):
    body = last_tweet_date = None
    max_id = None
    kwargs['count'] = 200

    resp = client.get('statuses/user_timeline', **kwargs)
    body = json.loads(resp.content)

    if not body:
        log.info('No body to load.')
        return

    if resp.status_code == 404:
        log.info('Message: {0}, Code: {1}'.format(body['errors']['message'],
                                                  body['errors']['code']))
        return

    if body:
        if last_update_date:
            last_tweet_date = dateutil.parser.parse(body[0]['created_at'])
            if last_tweet_date <= last_update_date:
                log.info('No new tweets.')
                return
        max_id = body[len(body) - 1]['id']

    if 'max_id' in kwargs:
        if max_id == kwargs['max_id']:
            log.info('Found an existing Id. Stopping update.')
            return
    kwargs['max_id'] = max_id

    for obj in body:
        tweet, created = Tweet.objects.get_or_create(
            created_at = parse(obj['created_at']),
            id_str = obj['id_str'],
            profile_image_url = obj['user']['profile_image_url'],
            tweet_id = obj['id'],
            text = obj['text'],
            user_id_str = obj['user']['id_str'],
            username = obj['user']['name'])

        Item.objects.create_or_update(
            instance = tweet,
            timestamp = tweet.created_at,
            source = __name__)

    _handle_tweets(client, **kwargs)
