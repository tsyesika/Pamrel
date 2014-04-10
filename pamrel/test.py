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

from django.test import TestCase

from pamrel.forms import PasteForm

class PasteTest(TestCase):

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
