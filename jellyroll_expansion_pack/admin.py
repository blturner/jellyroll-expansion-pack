from django.contrib import admin

from jellyroll_expansion_pack.models import Book, BookProgress, Shot


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published')


class ShotAdmin(admin.ModelAdmin):
    list_display = ('title', 'player',)


admin.site.register(Shot, ShotAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookProgress)
