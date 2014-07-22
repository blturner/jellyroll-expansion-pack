from django.contrib import admin

from jellyroll_expansion_pack.models import Book, BookProgress, Shot, Tweet


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published')


class ShotAdmin(admin.ModelAdmin):
    list_display = ('title', 'player',)


class TweetAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')


admin.site.register(Book, BookAdmin)
admin.site.register(BookProgress)
admin.site.register(Shot, ShotAdmin)
admin.site.register(Tweet, TweetAdmin)
