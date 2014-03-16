import datetime

from pytz import utc

from django.db import models
from django.core import urlresolvers

class Paste(models.Model):

    content = models.TextField()
    theme = models.CharField(max_length=256, default="github")
    language = models.CharField(max_length=256, blank=True, null=True, default='PlainText')
    delete_token = models.CharField(max_length=512)

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
        return hex(self.id).lstrip("0x").rstrip("L")

    def serialize(self):
        """ Convert model to serializable object (dict) """
        context = {
            "id": self.pid,
            "content": self.content,
            "theme": self.theme,
            "language": self.language,
            "token": self.delete_token,

            "delete_at": self.delete_at,
            "delete_on_views": self.delete_on_views,
            "numbers": self.numbers,
            "syntax": self.syntax,

            "created": self.created,
            "modified": self.modified,
        }

        for key, value in context.items():
            if isinstance(value, datetime.datetime):
                context[key] = value.isoformat()

        return context

    def get_absolute_url(self):
        return urlresolvers.reverse('paste', kwargs={'pk': self.pid})

    def validate(self):
        """ Checks this doesn't have delete on <x> that has been met """
        if self.delete_on_views is not None and self.delete_on_views < self.viewed:
            return False # too many views

        now = datetime.datetime.now(utc)
        if self.delete_at is not None and self.delete_at < now:
            return False # older than it should be

        return True

