from django.db.models import QuerySet, Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from post.models import Post
from post.permissions import IsAuthor
from post.serializers import PostListSerializer, PostDetailSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self) -> PostSerializer:
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Post.objects.prefetch_related("likes", "comments")
        if self.action in ("retrieve", "list"):
            queryset = queryset.filter(
                Q(author=self.request.user)
                | Q(author__id__in=self.request.user.followings.values("user_id"))
            )
        else:
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
