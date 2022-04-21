from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    list_filter = ('title',)
    search_fields = ('description',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created',)
    list_editable = ('text',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Comment, CommentAdmin)
