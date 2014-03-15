#!/usr/bin/python
from django import forms
from pamrel import models

from pygments import lexers

class PasteForm(forms.ModelForm):
	""" Form to create a paste """

	language = forms.ChoiceField(
		required=False,
		choices=(('', 'Auto Detect'),)
	)

	class Meta:
		model = models.Paste
		fields = ["content"]

	def __init__(self, initial=None, *args, **kwargs):
		super(PasteForm, self).__init__(initial=initial, *args, **kwargs)
		# Load all the choices for the languages pygments currently supports
		languages = dict(((lexer[0], lexer[1][0]) for lexer in lexers.get_all_lexers()))
		sorted_languages = languages.keys()
		sorted_languages.sort()
		self.fields['language'].choices += ((languages[name], name) for name in sorted_languages)
		self.fields['content'].widget.attrs.update({'placeholder': '<code> ... </code>'})

	def detect_language(self, data):
		""" Detects the language of the paste """
		try:
			lexer = lexers.guess_lexer(data)
		except Exception:
			return "PlainText"

		# for some unknown reason get_lexer_by_name(lexer.name) doesn't work >.>
		# however get_lexer_by_name(lexer.aliases[0]) does.
		return lexer.aliases[0]

	def save(self, *args, **kwargs):
		obj = super(PasteForm, self).save(*args, **kwargs)

		# Set language.
		if not self.cleaned_data.get("language", ""):
			obj.language = self.detect_language(self.cleaned_data["content"])
		else:
			obj.language = self.cleaned_data['language']

		# If we don't know the language, don't try syntax highlighting (duh!)
		if obj.language == "PlainText":
			obj.syntax = False
		else:
			obj.syntax = True

		obj.save()
		return obj
