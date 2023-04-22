from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, BasePermission

from post.models import Post, Comment
from post.permissions import IsAuthor
from post.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostSerializer,
    CommentSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self) -> PostSerializer:
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Post.objects.prefetch_related("likes", "comments")
        hashtag = self.request.query_params.get("hashtag")

        if self.action in ("retrieve", "list"):
            queryset = queryset.filter(
                Q(author=self.request.user)
                | Q(author__id__in=self.request.user.followings.values("user_id"))
            )

            if hashtag:
                queryset = queryset.filter(hashtag__icontains=hashtag)
        else:
            queryset = queryset.filter(author=self.request.user)

        return queryset

    def get_permissions(self) -> list[BasePermission]:
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommentSerializer
    lookup_field = "id"

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user, post=post)

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "destroy":
            return [IsAuthor()]
        return [IsAuthenticated()]

    def get_queryset(self) -> QuerySet:
        return Comment.objects.select_related("author", "post").filter(
            Q(post__author=self.request.user)
            | Q(post__author_id__in=self.request.user.followings.values("user_id"))
        )
