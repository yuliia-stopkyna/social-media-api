from celery.schedules import crontab
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.utils import aware_utcnow

from social_media_api.celery import app


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        daily_clean_tokens.s(),
    )


@app.task
def daily_clean_tokens():
    OutstandingToken.objects.filter(expires_at__lte=aware_utcnow()).delete()
