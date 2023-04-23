import datetime

from post.models import Post
from social_media_api.celery import app


@app.task
def create_post(
    post_id: int,
    schedule_time: datetime
) -> None:
    Post.objects.filter(pk=post_id).update(created_at=schedule_time, is_displayed=True)
