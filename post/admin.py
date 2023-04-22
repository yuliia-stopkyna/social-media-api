from django.contrib import admin

from post.models import Post, Like, Comment

admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
