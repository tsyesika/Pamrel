##
# Copyright (C) 2014 Jessica Tallon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

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
