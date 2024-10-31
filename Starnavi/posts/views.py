import threading
from datetime import datetime
from ninja import NinjaAPI, Query
from typing import List, Dict, Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from posts.models import Post, Comment
from posts.services import (
    create_jwt_token, jwt_required, moderate_content,
    send_auto_reply,register_user, authenticate_user)

from posts.schemas import (
    PostIn, PostOut, CommentIn,
    CommentOut, UserRegistration,
    UserResponse, Token, UserLogin
    )


api = NinjaAPI()


@api.post("/register/", response=UserResponse)
def register(
            request: Any,
            payload: UserRegistration,
            ) -> JsonResponse:

    """

    Register a new user.

    This endpoint allows a user to register by providing a username
    and password. A new user will be created in the system.


    """

    try:
        user = register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({
                "id": user.id,
                "username": user.username,
                "email": user.email},
                status=201)


@api.post("/login/", response=Token)
def login(
        request: Any,
        payload: UserLogin,
        ) -> Dict[str, Any]:

    """

    Log in a user.

    This endpoint allows a user to log in by providing their username
    and password. A JWT token will be returned if the credentials are valid.

    """

    try:
        user = authenticate_user(payload.username, payload.password)

    except ValueError as e:

        return {"error": str(e)}, 400

    except ObjectDoesNotExist:

        return {"error": "User does not exist."}, 400

    token = create_jwt_token(user)
    return {"token": token}


@api.post("/posts/", response=PostOut)
@jwt_required
def create_post(
            request: Any,
            payload: PostIn,
            ) -> JsonResponse:

    """

    Create a new blog post with optional automatic reply settings.

    This endpoint allows users to create a blog post, including settings for
    automatic replies if desired.


    """

    is_blocked = moderate_content(payload.content)

    post = Post.objects.create(
        title=payload.title,
        content=payload.content,
        author=request.user,
        is_blocked=is_blocked,
        auto_reply_enabled=payload.auto_reply_enabled,
        auto_reply_delay=payload.auto_reply_delay,
        auto_reply_text=payload.auto_reply_text,
    )

    return JsonResponse(
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.isoformat(),
            "is_blocked": post.is_blocked,
        },
        status=201
    )


@api.get("/posts/", response=List[PostOut])
@jwt_required
def list_posts(request: Any) -> List[PostOut]:

    """

    Retrieve a list of all blog posts.

    This endpoint returns all blog posts in the system.

    """

    return Post.objects.all()


@api.post("/posts/{post_id}/comments/", response=CommentOut)
@jwt_required
def create_comment(request: Any,
                   post_id: int,
                   payload: CommentIn,
                   ) -> JsonResponse:

    """

    Create a new comment on a blog post.

    This endpoint allows a user to add a comment to a specified blog post.
    The comment will be associated with the currently authenticated user.


    """

    is_blocked = moderate_content(payload.content)

    post = get_object_or_404(Post, id=post_id)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=payload.content,
        is_blocked=is_blocked,
    )

    threading.Thread(target=send_auto_reply, args=(comment.id,)).start()

    return JsonResponse(
        CommentOut.from_orm(comment).dict(),
        status=201
    )


@api.get("/posts/{post_id}/comments/", response=List[CommentOut])
@jwt_required
def list_comments(
                request: Any,
                post_id: int,
                ) -> List[CommentOut]:
    """
    Retrieve a list of comments for a specific blog post.

    This endpoint returns all comments associated with the specified post.

    """

    comments = Comment.objects.filter(post_id=post_id)
    return [CommentOut.from_orm(comment) for comment in comments]


@api.get("/comments-daily-breakdown/")
@jwt_required
def comments_daily_breakdown(request: Any, 
                             date_from: str = Query(...), 
                             date_to: str = Query(...)) -> Dict[str, int]:

    """

    Retrieve a daily breakdown of comments within a specified date range.

    This endpoint returns the total number of comments and the number of
    blocked comments created between the provided dates.

    """

    try:
        date_from_dt = datetime.fromisoformat(date_from)

        date_to_dt = datetime.fromisoformat(date_to)

    except ValueError:

        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    comments = Comment.objects.filter(created_at__range=(
                                            date_from_dt,
                                            date_to_dt))

    total_comments = comments.count()

    blocked_comments = comments.filter(is_blocked=True).count()

    return {
        "total_comments": total_comments,
        "blocked_comments": blocked_comments,
    }
