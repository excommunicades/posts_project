"""
admin.py

This module is used to register the Post and Comment
models with the Django admin site,
allowing for easy management of blog posts and comments
through the admin interface.

"""


from django.contrib import admin

from .models import Post, Comment

admin.site.register(Post)
admin.site.register(Comment)
