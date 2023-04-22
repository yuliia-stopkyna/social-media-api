from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet, CommentViewSet

app_name = "post"

router = routers.DefaultRouter()
router.register("", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:post_id>/comments/",
        CommentViewSet.as_view(actions={"get": "list", "post": "create"}),
        name="comment-list",
    ),
    path(
        "<int:post_id>/comments/<int:id>/",
        CommentViewSet.as_view(actions={"get": "retrieve", "delete": "destroy"}),
        name="comment-detail",
    ),
]
