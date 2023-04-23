from rest_framework import serializers

from post.models import Post, Like, Comment


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "user")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "author", "text", "created_at")
        read_only_fields = ("id", "author", "post", "created_at")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "created_at", "author", "content", "image", "hashtag")
        read_only_fields = ("id", "created_at", "author")


class PostScheduleSerializer(serializers.ModelSerializer):
    schedule_time = serializers.DateTimeField(
        required=True, source="created_at"
    )

    class Meta:
        model = Post
        fields = ("id", "schedule_time", "author", "content", "image", "hashtag", "is_displayed")
        read_only_fields = ("id", "author", "is_displayed")

    def create(self, validated_data):
        validated_data["is_displayed"] = False
        return Post.objects.create(**validated_data)


class PostListSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "author",
            "content",
            "image",
            "hashtag",
            "likes_number",
            "comments_number",
        )


class PostDetailSerializer(PostSerializer):
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "author",
            "content",
            "image",
            "hashtag",
            "likes",
            "comments",
        )
