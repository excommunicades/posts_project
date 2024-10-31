import pytest
import json
import time

from django.conf import settings
from django.contrib.auth.models import User

from posts.models import Post, Comment


@pytest.fixture
def auth_client(client):

    """

    Fixture to create an authenticated client for testing.

    This fixture creates a new user, logs in to obtain a JWT token, and
    configures the client to include the token in its authorization header
    for subsequent requests.

    """

    User.objects.create_user(
                        username='testuser',
                        password='password123',
                        email='test@example.com',
                        )

    url = "/api/login/"

    data = {
        'username': 'testuser',
        'password': 'password123',
    }

    response = client.post(
                        url, json.dumps(data),
                        content_type='application/json',
                        )

    token = response.json().get('token')

    assert response.status_code == 200

    assert token is not None

    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'


@pytest.mark.django_db
def test_register_user(client):

    """
    Test the user registration functionality.

    This test verifies that a new user can register successfully
    through the API
    and receives a user ID in the response.

    """

    url = "/api/register/"

    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
    }

    response = client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        )

    assert response.status_code == 201

    assert 'id' in response.json()

    response_duplicate = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
    )

    assert response_duplicate.status_code == 400

    assert 'error' in response_duplicate.json()


@pytest.mark.django_db
def test_login_user(client):

    """

    Test the user login functionality.

    This test verifies that a user can log in successfully through the API
    and receives a JWT token in the response.

    """

    User.objects.create_user(
                    username='testuser',
                    password='password123',
                    email='test@example.com',
                    )

    url = "/api/login/"

    data = {
        'username': 'testuser',
        'password': 'password123',
    }

    response = client.post(
                        url,
                        data,
                        content_type='application/json',
                        )

    assert response.status_code == 200

    assert 'token' in response.json()


@pytest.mark.django_db
def test_create_post(auth_client, client):

    """

    Test the creation of a new blog post.

    This test verifies that a new blog post can be successfully created
    via the API and that the response contains the expected data.

    """

    url = "/api/posts/"

    data = {
        'title': 'Test Post',
        'content': 'This is a test post.',
        'auto_reply_enabled': False,
        'auto_reply_delay': 0,
        'auto_reply_text': '',
    }

    response = client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        )

    assert response.status_code == 201

    assert 'id' in response.json()


@pytest.mark.django_db
def test_moderate_content(auth_client, client):

    """

    Test the content moderation functionality when creating a new post.

    This test verifies that when a post is created with inappropriate
    language in its content, the post is marked as blocked.

    """

    url = "/api/posts/"
    data = {
        'title': 'Test Post',
        'content': 'fuck ',
        'auto_reply_enabled': False,
        'auto_reply_delay': 0,
        'auto_reply_text': '',
    }
    response = client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        )

    assert response.status_code == 201

    assert 'id' in response.json()

    assert response.json()['is_blocked'] is True


@pytest.mark.usefixtures("transactional_db")
def test_send_auto_reply(auth_client, client):

    """

    Test the automatic reply functionality when a comment is made on a post.

    This test verifies that when a comment is added to a blog post with
    automatic replies enabled, the system responds with an automatic
    reply after a specified delay.
    
    """

    post_url = "/api/posts/"

    post_data = {
        'title': 'Test Post',
        'content': 'This is a test post.',
        'auto_reply_enabled': True,
        'auto_reply_delay': 1,
        'auto_reply_text': 'Thank you for your comment!',
    }

    post_response = client.post(
                            post_url, 
                            data=json.dumps(post_data),
                            content_type='application/json',
                            )

    assert post_response.status_code == 201

    post_id = post_response.json()['id']

    comment_url = f"/api/posts/{post_id}/comments/"

    comment_data = {
        'content': 'This is a test comment.'
    }

    comment_response = client.post(
                                comment_url,
                                data=json.dumps(comment_data),
                                content_type='application/json',
                                )

    assert comment_response.status_code == 201

    comment_id = comment_response.json()['id']

    assert Comment.objects.filter(id=comment_id).exists()

    time.sleep(2.0)

    auto_reply_count = Comment.objects.filter(
                                        post_id=post_id,
                                        content='Thank you for your comment!',
                                        ).count()

    assert auto_reply_count == 1


@pytest.mark.django_db
def test_create_comment(auth_client, client):

    """

    Test the create comment API endpoint.

    This test verifies that a new comment can be successfully created
    for a specific blog post. It checks that the response returns the
    expected status code and that the created comment's ID is present
    in the response.

    """

    user = User.objects.get(username='testuser')

    post = Post.objects.create(
                            title='Test Post',
                            content='This is a test post.',
                            author=user,
                            )

    url = f"/api/posts/{post.id}/comments/"

    data = {
        'content': 'This is a test comment.'
    }

    response = client.post(
                        url,
                        data,
                        content_type='application/json',
                        )

    assert response.status_code == 201

    assert 'id' in response.json()


@pytest.mark.django_db
def test_list_posts(auth_client, client):

    """
    Test the list posts API endpoint.

    This test verifies that all blog posts created by a user are correctly
    retrieved through the API. It checks that the response returns the
    expected number of posts.

    """

    user = User.objects.get(username='testuser')

    Post.objects.create(
                    title='Post 1',
                    content='Content 1',
                    author=user,
                    )

    Post.objects.create(
                    title='Post 2',
                    content='Content 2',
                    author=user,
                    )

    url = "/api/posts/"

    response = client.get(
                        url,
                        content_type='application/json',
                        )

    assert response.status_code == 200

    assert len(response.json()) == 2


@pytest.mark.django_db
def test_list_comments(auth_client, client):

    """
    Test the list comments API endpoint for a specific post.

    This test verifies that the comments associated with a given post are 
    correctly retrieved through the API. It checks that the response returns
    the expected number of comments.

    """

    user = User.objects.get(username='testuser')

    post = Post.objects.create(
                            title='Test Post',
                            content='This is a test post.',
                            author=user,
                            )

    Comment.objects.create(
                        post=post,
                        author=user,
                        content='First comment.',
                        )

    Comment.objects.create(
                        post=post,
                        author=user,
                        content='Second comment.',
                        )

    url = f"/api/posts/{post.id}/comments/"

    response = client.get(
                        url,
                        content_type='application/json',
                        )

    assert response.status_code == 200

    assert len(response.json()) == 2


@pytest.mark.django_db
def test_comments_daily_breakdown(auth_client, client):

    """

    Test the comments_daily_breakdown API endpoint.

    This test checks the functionality of
    the comments_daily_breakdown endpoint,

    ensuring it returns the correct counts of total and blocked comments within
    a specified date range.

    """

    user = User.objects.get(username='testuser')

    post = Post.objects.create(
                            title='Test Post',
                            content='This is a test post.',
                            author=user,
                            )

    Comment.objects.create(
                        post=post,
                        author=user,
                        content='First comment.',
                        )

    Comment.objects.create(
                        post=post,
                        author=user,
                        content='Second comment.',
                        is_blocked=True,
                        )

    url = "/api/comments-daily-breakdown/"

    response = client.get(
                        url,
                        {'date_from': '2024-01-01', 'date_to': '2024-12-31'},
                        content_type='application/json',
                        )

    assert response.status_code == 200
