import jwt
import functools
from datetime import timedelta, timezone
from time import sleep
from typing import Callable, Any
from better_profanity import profanity

from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import authenticate

from posts.models import Comment


def create_jwt_token(user: User) -> str:

    """

    Generate a JWT token for the given user.

    This function creates a JSON Web Token (JWT) that includes the user's ID 
    and an expiration time set for 24 hours from the current time.

    """

    exp_time = timezone.now() + timedelta(days=1)

    payload: dict[str, Any] = {
        'user_id': user.id,
        'exp': exp_time,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')



def jwt_required(func: Callable) -> Callable:

    """
    Decorator to protect views requiring JWT authentication.

    """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('Authorization')

        if token is None:
            return JsonResponse({'error': 'Token is missing'}, status=401)

        try:
            payload = jwt.decode(token.split()[1], settings.SECRET_KEY, algorithms=['HS256'])
            request.user = User.objects.get(id=payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return func(request, *args, **kwargs)

    return wrapper


def moderate_content(content: str) -> bool:

    """
    Checks if the provided text contains profanity.

    This function uses the better-profanity library

    """

    profanity.load_censor_words()

    return profanity.contains_profanity(content)


def send_auto_reply(comment_id: int) -> None:

    """
    Send an automatic reply to a comment based
                on the associated post's settings.

    """

    comment = Comment.objects.get(id=comment_id)
    post = comment.post

    if post.auto_reply_enabled:
        sleep(post.auto_reply_delay)

        reply_content = post.auto_reply_text

        Comment.objects.create(
            post=post,
            author=post.author,
            content=reply_content
        )


def register_user(username: str, email: str, password: str) -> User:

    """

    Register a new user.

    """

    if User.objects.filter(username=username).exists():

        raise ValidationError("Username already exists.")

    if User.objects.filter(email=email).exists():

        raise ValidationError("Email already exists.")

    return User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            )


def authenticate_user(username: str, password: str) -> User:

    """

    Authenticate a user by username and password.

    """

    user = authenticate(username=username, password=password)

    if user is None:

        if not User.objects.filter(username=username).exists():

            raise ObjectDoesNotExist("User does not exist.")

        else:
            raise ValueError("Invalid password.")

    return user
