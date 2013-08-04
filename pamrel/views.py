import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from pygments import highlight
from pygments.lexers import (guess_lexer, get_lexer_by_name, get_lexer_for_filename,
                             get_lexer_for_mimetype)
from pygments.formatters import HtmlFormatter

from pamrel.tools import render_to_json, random_token, deletable
from pamrel.models import Paste

@csrf_exempt
def delete_paste(request, paste):
    try:
        paste = int(paste, 16)
    except ValueError:
        error = {"Error": "Invalid ID {0!r}".format(paste)}
        return render_to_json(error, status=400)

    try:
        paste = Paste.objects.get(id=paste)
    except exceptions.ObjectDoesNotExist:
        error = {"Error": "Paste does not exist."}
        return render_to_json(error, status=404)

    try:
        token = json.loads(request.body)
    except:
        token = request.body

    if paste.delete_token != token:
        error = {"error": "Incorrect delete token"}
        return render_to_json(error, status=403)
    else:
        context = {
            "Verb": "delete",
            "Object":{
                "Id": paste.pid,
                "ObjectType": "paste",
            },
        }
        paste.delete()
        return render_to_json(context)



@csrf_exempt
def paste(request, pid=None):
    if request.method == "DELETE":
        return delete_paste(request, pid)

    if pid is not None and request.method == "GET":
        pid = int(pid, 16)
        try:
            paste = Paste.objects.get(id=pid)
        except ObjectDoesNotExist:
            error = {
                "Error": "Paste does not exist.",
            }
            return render_to_json(error, status=404)

        if deletable(paste):
            paste.delete()
            error = {"Error": "Paste does not exist."}
            return render_to_json(error, status=404)

        paste.viewed += 1
        paste.save()

        highlighted = False
        if paste.language is not None and paste.syntax:
            lexer = get_lexer_by_name(paste.language)
            numbers = "table" if paste.numbers else False
            paste.content = highlight(
                    paste.content,
                    lexer, 
                    HtmlFormatter(
                        linenos=numbers,
                        ),
                    )
            highlighted = True


        context = {
            "paste": paste,
            "highlighted": highlighted,
        }

        return render(request, "paste.html", context)

    elif pid != None and request.method == "POST":
        error = {
            "error": "You can't specify a paste ID when making a new post.",
        }

        return render_to_json(error, status=400)

    elif request.method == "POST":
        # making a new paste :D
        if request.POST:
            body = dict(request.POST)
        else:
            data = request.body
            try:
                body = json.loads(data)
            except ValueError:
                body = {"Content": data}

        body = body.get("Object", body)

        if len(body) <= 1 and "Content" not in body:
            body = {"Content": body.keys()[0]}

        if "Content" not in body:
            error = {"Error": "You need to specify content."}
            return render_to_json(error, status=400)

        content = body["Content"]
        if type(content) == list:
            content = content[0]

        # got to figure out what language it is
        if body.get("MimeType", None):
            lexer = get_lexer_for_mimetype(body["MimeType"]) 
        elif body.get("FileName", None):
            lexer = get_lexer_for_filename(body["FileName"])
        elif body.get("FileExtension", None):
            lexer = get_lexer_for_filename(
                    "file.{0}".format(body["FileExtension"]),
                    content
                    )
        else:
            lexer = guess_lexer(content)

        if "DeleteAt" in body:
            date_format = body.get("DateFormat", "%Y-%M-%DT%H:%MZ")
            date_at = datetime.datetime.strptime(body["DeleteAt"], date_format)
        else:
            delete_at = None

        paste = Paste(
            content=content,
            language=lexer.aliases[0], # for some strange reason get_lexer_by_name(lexer.name) does not work >.<
            delete_on_views=body.get("DeleteOnViews", None),
            delete_at=delete_at,
            syntax=body.get("Syntax", True),
            numbers=body.get("Numbers", False),
            delete_token=random_token(128),
            )
        
        if "Theme" in body and body["Theme"]:
            paste.theme = body["Theme"]

        paste.save()

        context = {
            "Verb": "post",
            "Object": {
                "Id": paste.pid,
                "ObjectType": "paste",
                "Content": paste.content,
                "Created": paste.created.isoformat(),
                "Modified": paste.modified.isoformat(),
                "Theme": paste.theme,
                "DeleteToken": paste.delete_token,
            },
        }

        return render_to_json(context)

@csrf_exempt
def api(request):
    if request.method == "DELETE":
        try:
            pasteid = json.loads(request.body)
        except ValueError:
            error = {"error": "Cannot decode request"}
            return render_to_json(error, status=400)
    
        pid = pasteid.get("object", {}).get("id", None)
        return delete_paste(pid)

    elif request.method != "GET":
        return paste(request)

    # Lets return the home page
    class Home(object):
        pid = "MANUAL"
        content = open(settings.HOME).read()
        numbers = False

    context = {
        "paste": Home(),
        "highlighted": True,
    }
    return render(request, "paste.html", context)

def licence(request):
    class Licence(object):
        pid = "LICENCE"
        content = open(settings.LICENCE).read()
        numbers = False

    context = {
        "paste": Licence(),
    }

    return render(request, "paste.html", context)
