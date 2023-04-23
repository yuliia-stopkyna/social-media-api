import os
import uuid

from django.conf import settings
from django.db import models


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"post-by-{instance.author.get_full_name()}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post_images/", filename)


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=post_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtag = models.CharField(max_length=100, null=True, blank=True)
    is_displayed = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Post {self.id} by {self.author}"

    @property
    def likes_number(self) -> int:
        return self.likes.count()

    @property
    def comments_number(self) -> int:
        return self.comments.count()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        unique_together = ("post", "user")

    def __str__(self) -> str:
        return f"Like to post {self.post.id} by {self.user}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Comment to post {self.post.id} by {self.author}"
