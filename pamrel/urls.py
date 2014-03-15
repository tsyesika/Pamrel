from django.conf.urls import patterns, include, url
from pamrel import views

urlpatterns = patterns("",
    url("^$", views.IndexView.as_view(), name="new"),
    url("^(?P<pk>\w+)/", include(patterns("",
        url("^$", views.PasteView.as_view(), name="paste"),
        url("^raw/$", views.RawPasteView.as_view(), name="raw"),
    ))),

    # API
    url('^api/v1/', include(patterns('',
        url('^languages/$', views.APILanguageListView.as_view(), name='api-languages'),
        url('^themes/$', views.APIThemeListView.as_view(), name='api-themes'),
        url('^(?P<pk>\w+)/', include(patterns('',
            url('^meta/$', views.APIMetaPasteView.as_view(), name='api-meta')
        ))),
    )))
)
