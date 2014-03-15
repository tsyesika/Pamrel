from django.conf.urls import patterns, include, url
from pamrel import views

urlpatterns = patterns("",
    url(r"^$", views.IndexView.as_view(), name="new"),
    url(r"^(?P<pk>\w+)/", include(patterns("",
        url("^$", views.PasteView.as_view(), name="paste"),
        url("^raw$", views.RawPasteView.as_view(), name="raw-paste"),
        url("^render$", views.RawPasteView.as_view(template_name="render.html"), name="render-paste"),
        url("^meta$", views.MetaPasteView.as_view(), name="meta-paste")
    )))
)
