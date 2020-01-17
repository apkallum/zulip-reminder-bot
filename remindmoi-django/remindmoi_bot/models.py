from django.db import models


class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)

    zulip_user_email = models.CharField(max_length=128)
    title = models.CharField(max_length=150)
    created = models.DateTimeField()
    deadline = models.DateTimeField()
    active = models.BooleanField(default=True)
