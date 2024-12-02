import pytest

from django.contrib.auth.models import User

from posts.services import create_jwt_token, moderate_content, send_auto_reply
from posts.models import Post, Comment


@pytest.mark.django_db
def test_create_jwt_token():

    """

    Test the creation of a JWT token for a user.

    """

    user = User.objects.create_user(
                            username='testuser',
                            password='testpass',
                            )

    token = create_jwt_token(user)

    assert isinstance(token, str)

    assert len(token) > 0 


@pytest.mark.django_db
def test_moderate_content_with_profanity():

    """

    Test the content moderation utility for detecting profanity.

    """

    assert moderate_content("This is a damn test") is True

    assert moderate_content("This is a clean test") is False


@pytest.mark.django_db
def test_send_auto_reply():

    """

    Test the automatic reply functionality for comments.

    """

    user = User.objects.create_user(
                            username='testuser',
                            password='testpass',
                            )

    post = Post.objects.create(
                    title="Test Post",
                    content="Test Content",
                    author=user,
                    auto_reply_enabled=True,
                    auto_reply_delay=1,
                    auto_reply_text="Thank you for your comment!",
                    )

    comment = Comment.objects.create(post=post, author=user, content="Great post!")

    send_auto_reply(comment.id)

    reply = Comment.objects.filter(post=post).exclude(id=comment.id).last()

    assert reply is not None

    assert reply.content == "Thank you for your comment!"

    assert reply.author == post.author
