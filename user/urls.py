from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from user.views import CreateUserView, ManageUserView, ReadUserView

app_name = "user"

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("register/", CreateUserView.as_view(), name="create"),
    path("profile/", ManageUserView.as_view(), name="update"),
    path("", ReadUserView.as_view(actions={"get": "list"}), name="user-list"),
    path("<int:pk>/", ReadUserView.as_view(actions={"get": "retrieve"}), name="user-detail")
]
