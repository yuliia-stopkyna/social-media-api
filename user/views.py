from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.serializers import UserCreateSerializer, UserUpdateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
