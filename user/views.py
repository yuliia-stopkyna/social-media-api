from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import UserFollower
from user.serializers import (
    UserCreateSerializer,
    UserUpdateSerializer,
    UserReadSerializer,
    UserFollowSerializer,
    UserReadProfileSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class ManageUserView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> settings.AUTH_USER_MODEL:
        return self.request.user

    def get_serializer_class(self) -> UserReadProfileSerializer | UserUpdateSerializer:
        if self.action == "retrieve":
            return UserReadProfileSerializer
        return UserUpdateSerializer


class UserPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReadUserView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = UserReadSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = UserPagination

    def get_queryset(self) -> QuerySet:
        queryset = get_user_model().objects.prefetch_related("followings", "followers")

        if self.action == "list":
            first_name = self.request.query_params.get("first_name")
            last_name = self.request.query_params.get("last_name")
            country = self.request.query_params.get("country")

            if first_name:
                queryset = queryset.filter(first_name__icontains=first_name)

            if last_name:
                queryset = queryset.filter(last_name__icontains=last_name)

            if country:
                queryset = queryset.filter(country__icontains=country)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type=str,
                description="Filter users by first name",
            ),
            OpenApiParameter(
                "last_name",
                type=str,
                description="Filter users by last name",
            ),
            OpenApiParameter(
                "country",
                type=str,
                description="Filter users by country",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserFollowView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        methods=["POST"], request=None, responses={200: UserReadProfileSerializer}
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
        url_name="user-follow",
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, pk=None) -> Response:
        """Endpoint for following user. Returns the profile data of the request user"""
        user_id = self.kwargs.get("pk")
        follower_id = self.request.user.id

        if user_id != follower_id:
            data = {"user": user_id, "follower": follower_id}
            serializer = UserFollowSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                read_serializer = UserReadProfileSerializer(self.request.user)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            data={"message": "User can't follow self"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        methods=["POST"], request=None, responses={200: UserReadProfileSerializer}
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
        url_name="user-unfollow",
        permission_classes=[IsAuthenticated],
    )
    def unfollow(self, request, pk=None) -> Response:
        """Endpoint for unfollowing user. Returns the profile data of the request user"""
        user_id = self.kwargs.get("pk")
        follower_id = self.request.user.id
        UserFollower.objects.filter(user_id=user_id, follower_id=follower_id).delete()
        read_serializer = UserReadProfileSerializer(self.request.user)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
