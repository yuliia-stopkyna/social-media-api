from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from post.models import Post, Comment, Like
from post.permissions import IsAuthor
from post.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self) -> PostSerializer:
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "like":
            return LikeSerializer
        return PostSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Post.objects.prefetch_related("likes", "comments")
        hashtag = self.request.query_params.get("hashtag")

        if self.action in ("retrieve", "list", "like", "unlike"):
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

    @extend_schema(
        methods=["POST"], request=None, responses={200: PostDetailSerializer}
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        url_name="post-like",
    )
    def like(self, request, pk=None) -> Response:
        """Endpoint for post like. Returns the post detail"""
        post = self.get_object()
        user = self.request.user
        serializer = LikeSerializer(
            data={"post": post.id, "user": user.id},
            initial={"post": post, "user": user},
        )

        if serializer.is_valid():
            serializer.save()
            read_serializer = PostDetailSerializer(self.get_object())
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=["POST"], request=None, responses={200: PostDetailSerializer}
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="unlike",
        url_name="post-unlike",
    )
    def unlike(self, request, pk=None) -> Response:
        """Endpoint for post unlike. Returns the post detail"""
        post = self.get_object()
        user = self.request.user
        Like.objects.filter(post=post, user=user).delete()
        read_serializer = PostDetailSerializer(self.get_object())
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "hashtag",
                type=str,
                description="Filter posts by hashtag",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
