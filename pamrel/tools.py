import json
import datetime
import random
import string

from pytz import utc

from django.http import HttpResponse

alphabet = string.ascii_lowercase + string.ascii_uppercase + "0123456789"
base = len(alphabet)

def render_to_json(data, status=200):
    """ Renders data to json """
    data = json.dumps(data)

    return HttpResponse(
            data,
            mimetype="application/json",
            status=status,
            )


def random_token(length):
    rstr = ""
    for i in range(length):
        rstr += random.choice(alphabet)
    return rstr

def deletable(paste):
    """ Determines if the paste should be deleted """
    if paste.delete_at is not None and datetime.datetime.now(utc) < paste.delete_at:
        return True

    if paste.delete_on_views is not None and paste.viewed >= paste.delete_on_views:
        return True

    return False
