from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
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
    PostScheduleSerializer,
)
from post.utils import schedule_post_display


class PostPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    pagination_class = PostPagination

    def get_serializer_class(self) -> PostSerializer:
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "like":
            return LikeSerializer
        if self.action == "schedule":
            return PostScheduleSerializer
        return PostSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Post.objects.prefetch_related("likes", "comments").filter(
            is_displayed=True
        )
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
        serializer = LikeSerializer(data={"post": post.id, "user": user.id})

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

    @action(
        methods=["POST"],
        detail=False,
        url_path="schedule",
        url_name="post-schedule",
    )
    def schedule(self, request, *args, **kwargs):
        """Endpoint for scheduling posts in UTC"""
        serializer = PostScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedule_time = request.POST["schedule_time"]
            serializer.validated_data["author"] = request.user
            post = serializer.save()
            schedule_post_display(schedule_time=schedule_time, post_id=post.id)
            serializer.data["schedule_time"] = schedule_time
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
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
