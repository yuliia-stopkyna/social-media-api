from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet

app_name = "post"

router = routers.DefaultRouter()
router.register("", PostViewSet, basename="post")

urlpatterns = [path("", include(router.urls))]
