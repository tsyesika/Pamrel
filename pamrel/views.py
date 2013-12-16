import json
import string
import random
import os

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from pygments import highlight
from pygments.lexers import (guess_lexer, get_lexer_by_name,
                             get_lexer_for_filename, get_lexer_for_mimetype)
from pygments.formatters import HtmlFormatter

from pamrel.models import Paste

class PasteView(DetailView):
    """ View for interacting with a Paste """

    template_name = "paste.html"
    model = Paste
    token_length = 128

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PasteView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        # Get an convert from base 16 -> base 10 the pk
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        if pk is None:
            return None
        try:
            pk = int(pk, 16)
        except ValueError:
            # Not a base 16 number
            return None
            
        try:
            obj = queryset.get(pk=pk)
        except ObjectDoesNotExist:
            return None

        return obj

    def get(self, *args, **kwargs):
        response = super(PasteView, self).get(*args, **kwargs)
        if isinstance(self.object, Paste):
            self.object.viewed += 1
            self.object.save()
        return response

    def post(self, request, *args, **kwargs):
        """ Makes a new Paste """
        data = {
            "content": "",
            "syntax": False,
            "numbers": True,
            "delete_at": None,
            "delete_on_views": 0,
            "language": None,
            "theme": "github",
            "delete_token": self.generate_token(self.token_length),
        }

        # We allow just data in order to easily post via curl
        try:
            raw_data = json.loads(request.body)
        except (ValueError, TypeError):
            content = request.POST.get("content", request.POST)
            raw_data = {"content": content}

        if not raw_data["content"]:
            # No POST data specified
            return self.json_response(
                {"error": "No content specified in Paste."},
                status=400
            )

        data["numbers"] = raw_data.get("numbers", data["numbers"])
        data["syntax"] = raw_data.get("syntax", data["syntax"])
        data["theme"] = raw_data.get("theme", data["theme"])
        data["content"] = raw_data["content"]

        # Figure out what language it is
        data["language"] = self.detect_language(raw_data)
        if data["language"] == "PlainText":
            # PlainText doesn't need syntax
            data["syntax"] = False


        if raw_data.get("deleteAt"):
            # Delete paste at this date!
            data_format = data.get("DateFormat", "%Y-%M-%DT%H:%MZ")
            data["delete_at"] = datetime.strptime(data["deleteAt"], date_format)
        
        paste = Paste(**data)
        paste.save()

        # If they've claimed to give them JSON we will give them JOSN back
        if request.META.get("CONTENT_TYPE").lower() == "application/json":
            serialized_data = paste.serialize()
            del serialized_data["content"]
            return self.json_response(serialized_data)
        else:
            return self.plain_response(request.build_absolute_uri(
                reverse("paste", kwargs={"pk": paste.pid})
            ))

    def generate_token(self, length):
        """ Generates a secure random token to allow access to Paste again """
        token = []
        alphabet = list(string.ascii_letters + string.digits + string.punctuation)
        for i in range(length):
            token += random.choice(alphabet)
        return "".join(token)

    def detect_language(self, data):
        """ Detects the language of the paste """
        try:
            if data.get("mimeType"):
                lexer = get_lexer_for_mimetype(data["mimeType"])
            elif data.get("fileName") or data.get("fileExtension"):
                data["fileName"] = "file.{0}".format(data["fileExtension"])
                lexer = get_lexer_for_filename(data["fileName"])
            else:
                lexer = guess_lexer(content)

        except Exception:
            # todo: find out exactly what exceptiosn it returns
            return "PlainText"
        
        # for some unknown reason get_lexer_by_name(lexer.name) doesn't work >.>
        # however get_lexer_by_name(lexer.aliases[0]) does.
        return lexer.aliases[0]

    def highlight_paste(self):
        """ Determines Lexer and highlights context """
        try:
            lexer = get_lexer_by_name(self.object.language)
        except Exception:
            return # todo: do something more useful than just return.
        numbers = "table" if self.object.numbers else False
        self.object.content = highlight(
            self.object.content,
            lexer, 
            HtmlFormatter(
                linenos=self.object.numbers,
            ),
        )

    def get_context_data(self, **kwargs):
        context = super(PasteView, self).get_context_data(**kwargs)
        if self.object is None:
            return {}

        context["theme_path"] = "{0}.css".format(self.object.theme)

        if self.object.language is not None:
            self.highlight_paste()
        else:
            context["highlighted"] = True

        return context

    def json_response(self, context, status=200):
        """ Returns a JSON response """
        if isinstance(context, dict):
            context = json.dumps(context)
        
        return HttpResponse(
            context,
            content_type="application/json",
            status=status
        )

    def plain_response(self, context, status=200):
        return HttpResponse(
            context+"\n",
            content_type="text/plain",
            status=status
        )

    def render_to_response(self, context, *args, **kwargs):
        if not context and self.object is None:
            # Somethings gone wrong, give our JSON 404
            return self.json_response(
                {"error": "Could not fine paste."},
                status=404
            )

        return super(PasteView, self).render_to_response(
            context=context,
            *args,
            **kwargs
        )
        

class RawPasteView(PasteView):
    """ Same as PasteView but returns unformatted paste as text/plain """

    def highlight_paste(self):
        return None

    def json_response(self, context, *args, **kwargs):
        if isinstance(context, basestring):
            try:
                context = json.loads(context)
            except ValueError:
                pass

        return self.plain_response(context, *args, **kwargs)

    def render_to_response(self, context, *args, **kwargs):
        if self.object is None:
            return self.plain_response("Error: Paste not found")
        
        return HttpResponse(
            self.object.content,
            content_type="text/plain",
        )

class FilePasteView(PasteView):
    """ Represents files as if they come from the DB as regular Pastes """
    
    path = None
    pid = None
    language = "PlainText"
    theme = "basic"
    highlighted = False
    numbers = False
    syntax = False

    def __init__(self, *args, **kwargs):
        super(FilePasteView, self).__init__(*args, **kwargs)
        if not os.path.isfile(self.path):
            self.content = "Could not find paste"
        else:
            self.content = open(self.path).read() 

    def get_object(self, queryset=None):
        if not os.path.isfile(self.path):
            return None # No object!

        class FilePaste(object):
            attrs = [
                "pid",
                "theme",
                "content",
                "language",
                "numbers",
                "syntax"
            ]
            
            def __init__(self, object, attrs=None):
                attrs = attrs or self.attrs
                for attr in attrs:
                    value = getattr(object, attr)
                    setattr(self, attr, value)
        
        return FilePaste(object=self)

    def get_context_data(self, **kwargs):
        context = super(FilePasteView, self).get_context_data(**kwargs)
        context["highlighted"] = self.highlighted
        return context

class IndexView(FilePasteView):
    """ Display the home/index page """
    pid = "MANUAL"
    path = settings.HOME
    highlighted = True

class LicenceView(FilePasteView):
    """ Display the AGPLv3 (Pamrel's licence) """
    pid = "LICENCE"
    path = settings.LICENCE
