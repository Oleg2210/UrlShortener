from django.db import models
from django.contrib.sessions.models import Session
from django.conf import settings


class ShortenedUrl(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, db_index=True, blank=False, null=False)
    shortened_id = models.CharField(max_length=settings.SHORTENED_MAX_LENGTH, null=False, blank=False, primary_key=True)
    link = models.URLField(max_length=settings.LINK_MAX_LENGTH, null=False, blank=False)


# Create your models here.
