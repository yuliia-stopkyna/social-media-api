from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from user.serializers import UserCreateSerializer, UserUpdateSerializer, UserReadSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ReadUserView(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserReadSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        queryset = get_user_model().objects.all()

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
