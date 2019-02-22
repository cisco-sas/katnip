# Copyright (C) 2019 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This file is part of Katnip.
#
# Katnip is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Katnip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Katnip.  If not, see <http://www.gnu.org/licenses/>.

from katnip.legos.http import HttpRequestLine
from bitstring import Bits
from test_model_low_level_field import ValueTestCase


class HttpRequestLineTests(ValueTestCase):

    __meta__ = False
    default_value = b'GET / HTTP/1.0\r\n'
    default_value_rendered = Bits(bytes=default_value)

    def setUp(self, cls=HttpRequestLine):
        super(HttpRequestLineTests, self).setUp(cls)

    def get_default_field(self, fuzzable=True):
        return self.cls(fuzzable=fuzzable, name=self.uut_name)

    def testMutateAllDifferent(self):
        """
        The issue is unclear, needs to fix this test
        """
        pass

    def testGetRenderedFields(self):
        """
        Irrelevant since this is a lego, which has internal fields
        """
        pass

    def testFuzzableMethod(self):
        req_no_fuzzable_method = HttpRequestLine(method=['GET', 'POST'])
        uut = HttpRequestLine(method=['GET', 'POST'], fuzzable_method=True)
        nfm_mutations = self.get_all_mutations(req_no_fuzzable_method)
        uut_mutations = self.get_all_mutations(uut)
        self.assertGreater(len(uut_mutations), len(nfm_mutations))
        self.assertTrue(any(b'POST' in x.bytes for x in uut_mutations))
        self.assertTrue(any(b'GET' in x.bytes for x in uut_mutations))
        self.assertFalse(any(b'POST' in x.bytes for x in nfm_mutations))

    def testFuzzableUri(self):
        default_uri = '/123'
        b_default_uri = default_uri.encode()
        req_no_fuzzable_uri = HttpRequestLine(uri=default_uri)
        uut = HttpRequestLine(uri=default_uri, fuzzable_uri=True)
        nfm_mutations = self.get_all_mutations(req_no_fuzzable_uri)
        uut_mutations = self.get_all_mutations(uut)
        self.assertGreater(len(uut_mutations), len(nfm_mutations))
        self.assertTrue(any(b_default_uri in x.bytes for x in uut_mutations))
        self.assertTrue(any(b_default_uri not in x.bytes for x in uut_mutations))
        self.assertTrue(all(b_default_uri in x.bytes for x in nfm_mutations))
