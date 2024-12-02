import pytest

from django.contrib.auth.models import User

from posts.models import Post, Comment


@pytest.mark.django_db
def test_post_creation():

    """

    Test the creation of a Post instance.

    """
    user = User.objects.create_user(
                            username='author',
                            password='testpass',
                            )

    post = Post.objects.create(
        title='Test Post',
        content='This is a test post.',
        author=user,
        auto_reply_enabled=True,
        auto_reply_delay=5,
        auto_reply_text='Thank you for your comment!',
    )

    assert post.title == 'Test Post'

    assert post.content == 'This is a test post.'

    assert post.author == user

    assert post.auto_reply_enabled is True

    assert post.auto_reply_delay == 5

    assert post.auto_reply_text == 'Thank you for your comment!'

    assert post.is_blocked is False


@pytest.mark.django_db
def test_comment_creation():

    """

    Test the creation of a Comment instance.

    """

    user = User.objects.create_user(
                            username='author',
                            password='testpass',
                            )

    post = Post.objects.create(
                        title='Test Post',
                        content='This is a test post.',
                        author=user,
                        )

    comment = Comment.objects.create(
        post=post,
        content='This is a test comment.',
        author=user
    )

    assert comment.content == 'This is a test comment.'

    assert comment.post == post

    assert comment.author == user

    assert comment.is_blocked is False


@pytest.mark.django_db
def test_post_string_representation():

    """

    Test the string representation of a Post instance.

    """

    user = User.objects.create_user(username='author', password='testpass')

    post = Post.objects.create(
                        title='Test Post',
                        content='This is a test post.',
                        author=user,
                        )

    assert str(post) == 'Test Post'


@pytest.mark.django_db
def test_comment_relationship():

    """

    Test the relationship between Comment and Post models.

    """

    user = User.objects.create_user(
                        username='author',
                        password='testpass',
                        )

    post = Post.objects.create(
                        title='Test Post',
                        content='This is a test post.',
                        author=user,
                        )

    comment = Comment.objects.create(
                            post=post,
                            content='This is a test comment.',
                            author=user,
                            )

    assert comment.post == post

    assert post.comments.count() == 1

    assert post.comments.first() == comment
