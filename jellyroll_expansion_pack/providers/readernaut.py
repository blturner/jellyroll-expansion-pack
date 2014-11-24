import logging
import urllib

import iso8601
import pytz

from datetime import datetime

from django.conf import settings

from jellyroll.models import Item
from jellyroll.providers import utils

from jellyroll_expansion_pack.models import Book, BookProgress


log = logging.getLogger('jellyroll_expansion_pack.providers.readernaut')


class ReadernautClient(object):
    def __init__(self, username, api_token, method='v1'):
        self.username, self.api_token = username, api_token
        self.method = method

    def __getattr__(self, method):
        return ReadernautClient(self.username, self.api_token, '{0}/{1}'.format(self.method, method))

    def __call__(self, **params):
        params['username'] = params['goal__user__username'] = self.username
        params['api_key'] = self.api_token
        url = ('http://readernaut.com/api/{0}?'.format(self.method)) + urllib.urlencode(params)
        return utils.getjson(url)


def enabled():
    return True


def update(force=False):
    readernaut = ReadernautClient(settings.READERNAUT_USERNAME,
                                  settings.READERNAUT_API_KEY)

    last_update_date = Item.objects.get_last_update_of_model(BookProgress)
    resp = readernaut.goals.progress(limit=50)
    last_post_date = utils.parsedate(resp['objects'][0]['created'])

    if not force and last_post_date <= last_update_date:
        log.info('Skipping update: last update date: {0}; last post date: {1}'.format(last_update_date, last_post_date))
        return

    offset = 0

    while offset < resp['meta']['total_count']:
        if resp['objects']:
            for obj in resp['objects']:
                _handle_goal(obj)

        offset += resp['meta']['limit']
        resp = readernaut.goals.progress(limit=resp['meta']['limit'],
                                         offset=offset)


def _handle_goal(obj):
    book_info = obj['goal']['book_edition']['book']
    edition_info = obj['goal']['book_edition']

    try:
        published = datetime.strptime(
            edition_info['published'], '%Y-%m-%d'
        ).replace(tzinfo=pytz.utc)
    except TypeError:
        published = None

    date_read = iso8601.parse_date(obj['date_read'])
    author = _handle_authors(book_info['authors'])

    book, book_created = Book.objects.get_or_create(
        title=book_info['title'],
        isbn=edition_info['isbn'],
        author=author,
        cover_image=edition_info['cover'],
        subtitle=edition_info['subtitle'],
        published=published,
        pages=edition_info['pages']
    )

    book_progress, created = BookProgress.objects.get_or_create(
        book = book,
        amount = obj['amount'],
        amount_read = obj['amount_read'],
        date_read = date_read,
        percent = obj['percent'],
        url = obj['resource_uri'])

    return Item.objects.create_or_update(
        instance = book_progress,
        timestamp = book_progress.date_read,
        source = __name__)


def _handle_authors(author_info):
    author_string = ''
    for i, author in enumerate(author_info):
        author_string += author['full_name']
        if i != (len(author_info) - 1):
            author_string += ', '
    return author_string
