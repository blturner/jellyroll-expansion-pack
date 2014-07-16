from django.db import models

from jellyroll.models import Item


class AbstractJellyrollModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'jellyroll'


class Book(AbstractJellyrollModel):
    title = models.CharField(max_length=255)
    author = models.CharField(blank=True, max_length=255)
    cover_image = models.URLField(blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    published = models.DateTimeField(blank=True, null=True)
    isbn = models.CharField(max_length=255)
    pages = models.IntegerField(blank=True, default=0)

    class Meta(AbstractJellyrollModel.Meta):
        ordering = ['title']

    def __unicode__(self):
        return self.title


class BookProgress(AbstractJellyrollModel):
    amount = models.PositiveIntegerField()
    amount_read = models.PositiveIntegerField()
    book = models.ForeignKey('Book')
    date_read = models.DateTimeField()
    percent = models.PositiveIntegerField()
    url = models.URLField()

    class Meta(AbstractJellyrollModel.Meta):
        ordering = ['-date_read']

    def __unicode__(self):
        return 'Read {0} pages of {1}'.format(self.amount, self.book.title)


class Shot(AbstractJellyrollModel):
    """
    A shot from dribbble.com.
    """
    shot_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    player = models.CharField(max_length=255)
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    likes_count = models.PositiveIntegerField()
    comments_count = models.PositiveIntegerField()
    rebounds_count = models.PositiveIntegerField()
    url = models.URLField()
    short_url = models.URLField()
    views_count = models.PositiveIntegerField()
    image_url = models.URLField()
    image_teaser_url = models.URLField()
    created_at = models.DateTimeField()

    def __unicode__(self):
        return self.title


Item.objects.follow_model(Shot)
Item.objects.follow_model(BookProgress)
