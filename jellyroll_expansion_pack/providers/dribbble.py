import dateutil
import logging

from django.conf import settings
from django.utils.timezone import utc

from jellyroll.models import Item
from jellyroll.providers import utils

from jellyroll_expansion_pack.models import Shot


log = logging.getLogger('jellyroll.providers.dribbble')
SHOTS_URL = 'http://api.dribbble.com/players/%s/shots'
LIKES_URL = 'http://api.dribbble.com/players/%s/shots/likes'


def enabled():
    ok = hasattr(settings, "DRIBBBLE_USERNAME")
    if not ok:
        log.warn('The Dribbble provider is not available because the '
                 'DRIBBBLE_USERNAME setting is undefined.')
    return ok


def update():
    _update_shots()


def _update_shots():
    last_update_date = Item.objects.get_last_update_of_model(Shot)

    resp = utils.getjson(SHOTS_URL % settings.DRIBBBLE_USERNAME)
    likes_resp = utils.getjson(LIKES_URL % settings.DRIBBBLE_USERNAME)

    page = 1

    # refactor this into a function and pass in resp and likes_resp
    while True:
        if page > resp['pages']:
            log.debug("Ran out of shots; stopping.")
            break

        for shot in resp['shots']:
            timestamp = dateutil.parser.parse(str(shot['created_at'])).replace(tzinfo=None)
            if settings.USE_TZ:
                timestamp = dateutil.parser.parse(str(shot['created_at'])).replace(tzinfo=utc)

            if timestamp < last_update_date:
                log.info("Hit an old shot, (created %s; last update was %s); stopping;", timestamp, last_update_date)
                break
            _handle_shot(shot)

        page += 1


def _handle_shot(shot):
    created_at = utils.parsedate(shot['created_at'])

    d, created = Shot.objects.get_or_create(
        shot_id = shot['id'],
        title = shot['title'],
        player = shot['player']['username'],
        height = shot['height'],
        width = shot['width'],
        likes_count = shot['likes_count'],
        comments_count = shot['comments_count'],
        rebounds_count = shot['rebounds_count'],
        url = shot['url'],
        short_url = shot['short_url'],
        views_count = shot['views_count'],
        image_url = shot['image_url'],
        image_teaser_url = shot['image_teaser_url'],
        created_at = created_at,
    )

    return Item.objects.create_or_update(
        instance = d,
        timestamp = created_at,
        source_id = shot['id'],
        source = __name__,
    )
