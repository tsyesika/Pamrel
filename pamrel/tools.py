import json
import datetime

from pytz import utc

from django.http import HttpResponse

def render_to_json(data, status=200):
    """ Renders data to json """
    data = json.dumps(data)

    return HttpResponse(
            data,
            mimetype="application/json",
            status=status,
            )


def deletable(paste):
    """ Determines if the paste should be deleted """
    if paste.delete_at is not None:
        if datetime.datetime.now(utc) < paste.delete_at:
            return True

    if paste.delete_on_views is not None:
        if paste.viewed >= paste.delete_on_views:
            return True

    return False
