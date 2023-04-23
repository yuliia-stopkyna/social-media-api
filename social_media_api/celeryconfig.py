broker_url = "redis://localhost:6379"
task_track_started = True
task_time_limit = 30 * 60
task_always_eager = True
beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
