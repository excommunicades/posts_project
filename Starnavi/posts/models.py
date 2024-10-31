from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):

    """
    Model representing a blog post.

    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_delay = models.IntegerField(default=0)
    auto_reply_text = models.TextField(blank=True, null=True)

    def __str__(self):

        """Return a string representation of the post."""

        return self.title


class Comment(models.Model):

    """

    Model representing a comment on a post.

    """

    post = models.ForeignKey(Post, related_name='comments',
                             on_delete=models.CASCADE)

    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
