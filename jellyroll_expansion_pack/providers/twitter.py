import base64
import json
import logging
import requests
import urllib

from dateutil.parser import parse

from django.conf import settings

from jellyroll.models import Item

from jellyroll_expansion_pack.models import Tweet


log = logging.getLogger('jellyroll_expansion_pack.providers.twitter')


class TwitterClient(object):
    def __init__(self, username, method="1.1"):
        self.username = username
        self.method = method

        self.api_token = self.set_api_token()

    def __getattr__(self, method):
        return TwitterClient(self.username,
                             '{0}/{1}'.format(self.method, method))

    def __call__(self, **kwargs):
        headers = {
            'authorization': '{0} {1}'.format(self.token_type, self.access_token)
        }

        kwargs['screen_name'] = self.username
        kwargs['count'] = 200

        url = ('https://api.twitter.com/{0}.json?'.format(self.method)) + \
            urllib.urlencode(kwargs)
        log.info(url)

        response = requests.get(url, headers=headers)

        return json.loads(response.content)

    def set_api_token(self):
        log.info('SET THE API TOKEN')
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

        token_type = api_token['token_type']
        access_token = api_token['access_token']

        return '{0} {1}'.format(token_type, access_token)


def enabled():
    return True


def update():
    kwargs = {}
    since_id = None
    tweet_items = Item.objects.get_for_model(Tweet)

    client = TwitterClient(settings.TWITTER_USERNAME)

    if tweet_items:
        since_id = Tweet.objects.get(id=tweet_items[0].object_id).tweet_id

    if since_id:
        kwargs['since_id'] = since_id
    _handle_tweets(client, **kwargs)


def _handle_tweets(client, **kwargs):
    resp = client.statuses.user_timeline(**kwargs)

    print resp

    if not resp:
        log.info('There was no response from the API endpoint.')
        return

    max_id = resp[len(resp) - 1]['id']

    if 'max_id' in kwargs:
        if max_id == kwargs['max_id']:
            log.info('Found an existing Id. Stopping update.')
            return
    kwargs['max_id'] = max_id

    for obj in resp:
        tweet, created = Tweet.objects.get_or_create(
            created_at = parse(obj['created_at']),
            id_str = obj['id_str'],
            tweet_id = obj['id'],
            text = obj['text'])

        Item.objects.create_or_update(
            instance = tweet,
            timestamp = tweet.created_at,
            source = __name__)

    _handle_tweets(client, **kwargs)
