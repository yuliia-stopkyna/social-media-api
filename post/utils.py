import datetime
import json
import uuid

from django_celery_beat.models import ClockedSchedule, PeriodicTask


def schedule_post_display(
    schedule_time: datetime,
    post_id: int
) -> None:
    schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=schedule_time)

    PeriodicTask.objects.create(
        clocked=schedule,
        one_off=True,
        name=f"Schedule post creation-{uuid.uuid4()}",
        task="post.tasks.create_post",
        args=json.dumps([post_id, schedule_time])
    )
