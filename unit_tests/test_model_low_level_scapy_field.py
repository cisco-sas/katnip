# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This module was authored and contributed by dark-lbp <jtrkid@gmail.com>
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

'''
Tests for Scapy field:
'''

from common import metaTest
from test_model_low_level_field import ValueTestCase
from bitstring import Bits
from katnip.model.low_level.scapy import *
from scapy.all import *


class ScapyFieldTests(ValueTestCase):

    __meta__ = False

    def setUp(self, cls=ScapyField):
        super(ScapyFieldTests, self).setUp(cls)
        self._fuzz_count = 2000
        self.seed = 1000
        random.seed(self.seed)
        self._fuzz_packet = IP(ttl=RandByte())
        self.default_value = str(IP(ttl=RandByte()))
        self.default_value_rendered = Bits(bytes=self.default_value)
        self.uut_name = 'ScapyFieldTest'


    def runTest(self):
        pass

    def get_default_field(self, fuzzable=True):
        return self.cls(value=self._fuzz_packet, fuzzable=fuzzable, name=self.uut_name, fuzz_count=self._fuzz_count, seed=self.seed)

    def _base_check(self, field):
        num_mutations = field.num_mutations()
        mutations = self._get_all_mutations(field)
        self.assertEqual(num_mutations, len(mutations))
        mutations = self._get_all_mutations(field)
        self.assertEqual(num_mutations, len(mutations))


    @metaTest
    def testMutateAllDifferent(self):
        # some time will got same data, so we skip this test.
        pass





