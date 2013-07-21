from django.conf.urls import patterns, include, url

urlpatterns = patterns("",
    url(r"^$", "pamrel.views.api", name="docs"),
    url(r"^(?P<pid>\w+)$", "pamrel.views.paste", name="paste"),
)
