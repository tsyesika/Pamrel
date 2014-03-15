import json
import string
import random
import os
import glob

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, CreateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

from pamrel.models import Paste
from pamrel.forms import PasteForm

class IndexView(CreateView):
    form_class = PasteForm
    model = Paste
    template_name = "new.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        # If they're a not pamrel.lu give them back the URL to the paste rather than a 302
        if self.request.POST.get("webUI") or self.request.method != "POST":
            # There must be a better way of detecting this =/
            return super(IndexView, self).form_valid(form=form, *args, **kwargs)

        self.object = form.save()
        return HttpResponse(
            content=self.request.build_absolute_uri(self.get_success_url()) + '\n',
            content_type="text/plain"
        )

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

    def increment_paste(self, object=None):
        """ Increments the viewed counter on a paste """
        if object is None:
            object = self.object

        if isinstance(self.object, Paste):
            object.viewed += 1
            object.save()
            return True

        return False

    def get(self, *args, **kwargs):
        response = super(PasteView, self).get(*args, **kwargs)
        self.increment_paste()
        return response

    def generate_token(self, length):
        """ Generates a secure random token to allow access to Paste again """
        token = []
        alphabet = list(string.ascii_letters + string.digits + string.punctuation)
        for i in range(length):
            token += random.choice(alphabet)
        return "".join(token)

    def highlight_paste(self):
        """ Determines Lexer and highlights context """
        try:
            lexer = lexers.get_lexer_by_name(self.object.language)
        except Exception:
            return self.object.content
        numbers = "table" if self.object.numbers else False
        return highlight(
            self.object.content,
            lexer,
            HtmlFormatter(
                linenos=self.object.numbers,
            ),
        )

    def get_context_data(self, **kwargs):
        context = super(PasteView, self).get_context_data(**kwargs)
        if self.object is None:
            return context

        context["content"] = self.object.content
        context["theme_path"] = "{0}.css".format(self.object.theme)

        if self.object.language != "PlainText":
            context["content"] = self.highlight_paste()
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
        if self.object is None:
            # Somethings gone wrong, give our JSON 404
            class Error(object):
                number = 404
                message = "Nothing to see here folks, move along now."
            context = {"error": Error()}
            self.template_name = "error.html"

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


##
# API views
##

class APIMetaPasteView(PasteView):
    """ Represents the attributes/meta data of a Paste as JSON """

    def increment_paste(self, object=None):
        """ Stop this incrementing the paste as meta isn't a view of it """
        return False

    def get_context_data(self, **kwargs):
        context = {
            "viewed": self.object.viewed,
            "created": self.object.created.isoformat(),
            "modified": self.object.modified.isoformat(),
            "syntax": self.object.syntax,
            "theme": self.object.theme,
            "language": self.object.language,
            "numbers": self.object.numbers,
        }

        if self.object.delete_at is not None:
            context["deleteAt"] = self.object.delete_at.isoformat()

        if self.object.delete_on_views != 0:
            context["deleteOnViews"] = self.object.delete_on_views

        return context

    def render_to_response(self, context):
        return self.json_response(context)

class APIThemeListView(View):
    """ List all themes on the pastebin """
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            json.dumps([name.split('.', 1)[0].split('/')[-1] for name in glob.glob(os.path.join(settings.STATIC_ROOT, 'themes', '*.css'))]),
            content_type="application/json"
        )

class APILanguageListView(View):
    """ List all themes pastebin has """

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            json.dumps(dict(((lexer[0], lexer[1][0]) for lexer in lexers.get_all_lexers()))),
            content_type="application/json"
        )
