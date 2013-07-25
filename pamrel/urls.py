from django.conf.urls import patterns, include, url

urlpatterns = patterns("",
    url(r"^$", "pamrel.views.api", name="docs"),
    url(r"^licence$", "pamrel.views.licence", name="licence"),
    url(r"^license$", "pamrel.views.licence", name="licence"),
    url(r"^(?P<pid>\w+)$", "pamrel.views.paste", name="paste"),
)
