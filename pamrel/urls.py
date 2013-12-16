from django.conf.urls import patterns, include, url
from pamrel.views import (PasteView, IndexView, LicenceView, RawPasteView,
                          MetaPasteView)

urlpatterns = patterns("",
    url(r"^$", IndexView.as_view(), name="index"),
    url(r"^licence$", LicenceView.as_view(), name="licence"),
    url(r"^license$", LicenceView.as_view(), name="license"),
    url(r"^(?P<pk>\w+)/", include(patterns("",
        url("^$", PasteView.as_view(), name="paste"),
        url("^raw$", RawPasteView.as_view(), name="raw-paste"),
        url("^render$", RawPasteView.as_view(template_name="render.html"), name="render-paste"),
        url("^meta$", MetaPasteView.as_view(), name="meta-paste")
    )))
)
