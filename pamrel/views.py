from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

from pamrel.tools import render_to_json, deletable
from pamrel.models import Paste

@csrf_exempt
def paste(request, pid=None):
    if pid is not None and request.method == "GET":
        pid = int(pid, 16)
        try:
            paste = Paste.objects.get(id=pid)
        except ObjectDoesNotExist:
            error = {
                "error": "Paste does not exist.",
            }
            return render_to_json(error, status=404)

        if deletable(paste):
            paste.delete()
            error = {"error": "Paste does not exist."}
            return render_to_json(error, status=404)

        paste.viewed += 1
        paste.save()

        highlighted = False
        if paste.language is not None and paste.syntax:
            lexer = get_lexer_by_name(paste.language)
            paste.content = highlight(paste.content, lexer, HtmlFormatter())
            highlighted = True

        context = {
            "paste": paste,
            "highlighted": highlighted,
        }

        return render(request, "paste.html", context)

    elif pid is not None and request.method == "POST":
        error = {
            "error": "You can't specify a paste ID when making a new post.",
        }

        return render_to_json(error, status=400)

    elif request.method == "POST":
        # making a new paste :D
        body = dict(request.POST)
        if len(body) <= 1 and "content" not in body:
            body = {"content": body.keys()[0]}

        if "content" not in body:
            error = {"error": "You need to specify content."}
            return render_to_json(error, status=400)

        content = body["content"]
        if type(content) == list:
            content = content[0]

        # got to figure out what language it is
        lexer = guess_lexer(content) 

        if "delete_at" in body:
            date_format = body.get("date_format", "%Y-%M-%DT%H:%MZ")
            date_at = datetime.datetime.strptime(body["delete_at"], date_format)
        else:
            delete_at = None

        paste = Paste(
            content=content,
            language=lexer.aliases[0], # for some strange reason get_lexer_by_name(lexer.name) does not work >.<
            delete_on_views=body.get("delete_on_views", None),
            delete_at=delete_at,
            syntax=body.get("syntax", True),
            numbers=body.get("numbers", True), 
            )
        
        paste.save()

        context = {
            "verb": "post",
            "object": {
                "id": paste.pid,
                "objectType": "paste",
                "content": paste.content,
                "created": paste.created.isoformat(),
                "modified": paste.modified.isoformat(),
            },
        }

        return render_to_json(context)

@csrf_exempt
def api(request):
    if request.method != "GET":
        return paste(request)


