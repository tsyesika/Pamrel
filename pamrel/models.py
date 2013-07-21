import datetime

from pytz import utc

from django.db import models

class Paste(models.Model):

    content = models.TextField()
    theme = models.CharField(max_length=256, default="base")
    language = models.CharField(max_length=256, blank=True, null=True, default=None)

    # optional stuff
    delete_at = models.DateTimeField(blank=True, null=True)
    delete_on_views = models.IntegerField(blank=True, null=True)
    numbers = models.BooleanField(default=False)
    syntax = models.BooleanField(default=True) 

    # properties
    viewed = models.IntegerField(default=0)
    created = models.DateTimeField(default=datetime.datetime.now(utc))
    modified = models.DateTimeField(default=datetime.datetime.now(utc)) 

    @property
    def pid(self):
        """ Goes from Paste.id -> base64 encoded string """
        return hex(self.id).lstrip("0x")
