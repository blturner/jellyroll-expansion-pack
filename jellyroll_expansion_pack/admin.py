from django.contrib import admin

from jellyroll_expansion_pack.models import Book, BookProgress, Shot


class ShotAdmin(admin.ModelAdmin):
    list_display = ('title', 'player',)


admin.site.register(Shot, ShotAdmin)
admin.site.register(Book)
admin.site.register(BookProgress)
