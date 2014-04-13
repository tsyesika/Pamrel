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
import json

from django.test import TestCase

from pamrel.forms import PasteForm

class PasteTest(TestCase):

    def __get_id(self, url):
        return url.split("/")[-2]

    def test_delete_on_views(self):
        """ Test that it will delete on <x> number of views """
        request = {
            "content": "This is the paste content",
            "delete_on_views": 3
        }

        response = self.client.post("/", request)
        self.assertEqual(response.status_code, 200)

        # Request 3 times ensuring we get a 200 response
        url = "/{id}/".format(id=self.__get_id(response.content))
        for i in range(request["delete_on_views"]):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # Now it should produce a 404 as it should be deleted
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_paste_utf8(self):
        """ Tests that you can post UTF-8 encoded paste data """
        # Build up list of ALL utf-8 characters
        # technically I think this should be up to 2**32 as utf-8 is 4 bytes
        # the unichr barfs at anything 0x10000 or higher.
        paste = u"".join([unichr(i) for i in range(0xffff)])
        response = self.client.post("/", {
            "content": paste
        })
        self.assertEqual(response.status_code, 200)
