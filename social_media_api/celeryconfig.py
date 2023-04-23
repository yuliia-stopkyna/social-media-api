broker_url = "redis://redis:6379"  # redis://localhost:6379 (without docker)
task_track_started = True
task_time_limit = 30 * 60
task_always_eager = True
beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
