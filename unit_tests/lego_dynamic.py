# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
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

from katnip.legos.dynamic import DynamicExtended, DynamicInt, DynamicString
from kitty.model import String
from kitty.model import BE32
from kitty.model import ENC_STR_BASE64

from common import BaseTestCase, get_mutation_set


class DynamicTestCase(BaseTestCase):

    def setUp(self):
        super(DynamicTestCase, self).setUp()
        self.def_value = '1234'
        self.the_key = 'the_key'


class DynamicExtendedTestCase(DynamicTestCase):
    '''
    Tests for the :class:`~katnip.legos.dynamic.DynamicExtended`
    '''

    def test_default_value(self):
        additional_field = String('the_string')
        uut = DynamicExtended(key=self.the_key, value=self.def_value, additional_field=additional_field)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)

    def test_vanilla_with_string(self):
        additional_field = String('the_string')
        uut = DynamicExtended(key=self.the_key, value=self.def_value, additional_field=additional_field)
        addional_mutations = get_mutation_set(additional_field)
        uut_mutations = get_mutation_set(uut)
        if not any(x in uut_mutations for x in addional_mutations):
            raise AssertionError('Not all addional_mutations are in uut_mutations')
        self.assertGreater(len(uut_mutations), len(addional_mutations))

    def test_set_session_data(self):
        additional_field = String(self.def_value)
        new_value = 'new_value'
        uut = DynamicExtended(key=self.the_key, value=self.def_value, additional_field=additional_field)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)
        uut.set_session_data({self.the_key: new_value})
        res = uut.render().bytes
        self.assertEqual(res, new_value)

    def test_not_fuzzable(self):
        additional_field = String('the_string')
        uut = DynamicExtended(key=self.the_key, value=self.def_value, additional_field=additional_field, fuzzable=False)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)
        self.assertEqual(uut.num_mutations(), 0)


class DynamicStringTestCase(DynamicTestCase):
    '''
    Tests for the :class:`~katnip.legos.dynamic.DynamicString`
    '''

    def test_default_value(self):
        uut = DynamicString(key=self.the_key, value=self.def_value)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)

    def test_vanilla(self):
        similar_string = String(self.def_value)
        uut = DynamicString(key=self.the_key, value=self.def_value)
        similar_mutations = get_mutation_set(similar_string)
        uut_mutations = get_mutation_set(uut)
        if not any(x in uut_mutations for x in similar_mutations):
            raise AssertionError('Not all similar_mutations are in uut_mutations')
        self.assertGreater(len(uut_mutations), len(similar_mutations))

    def test_vanilla_with_encoder(self):
        similar_string = String(self.def_value, encoder=ENC_STR_BASE64)
        uut = DynamicString(key=self.the_key, value=self.def_value, encoder=ENC_STR_BASE64)
        similar_mutations = get_mutation_set(similar_string)
        uut_mutations = get_mutation_set(uut)
        if not any(x in uut_mutations for x in similar_mutations):
            raise AssertionError('Not all similar_mutations are in uut_mutations')
        self.assertGreater(len(uut_mutations), len(similar_mutations))

    def test_limited_string(self):
        similar_string = String(self.def_value, max_size=len(self.def_value))
        uut = DynamicString(key=self.the_key, value=self.def_value, keep_size=True)
        similar_mutations = get_mutation_set(similar_string)
        uut_mutations = get_mutation_set(uut)
        if not any(x in uut_mutations for x in similar_mutations):
            raise AssertionError('Not all similar_mutations are in uut_mutations')
        self.assertGreater(len(uut_mutations), len(similar_mutations))
        if any(len(x) != len(self.def_value) for x in uut_mutations):
            raise AssertionError('There are results with different size than the default value')

    def test_set_session_data(self):
        new_value = 'new_value'
        uut = DynamicString(key=self.the_key, value=self.def_value)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)
        uut.set_session_data({self.the_key: new_value})
        res = uut.render().bytes
        self.assertEqual(res, new_value)

    def test_not_fuzzable(self):
        uut = DynamicString(key=self.the_key, value=self.def_value, fuzzable=False)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)
        self.assertEqual(uut.num_mutations(), 0)


class DynamicIntTestCase(DynamicTestCase):
    '''
    Tests for the :class:`~katnip.legos.dynamic.DynamicInt`
    '''
    def setUp(self):
        super(DynamicIntTestCase, self).setUp()
        self.bf = BE32(1234)
        self.def_value = self.bf.render().bytes

    def test_default_value(self):
        uut = DynamicInt(self.the_key, self.bf)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)

    def test_set_session_data(self):
        new_value = 'new_value'
        uut = DynamicInt(self.the_key, self.bf)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)
        uut.set_session_data({self.the_key: new_value})
        res = uut.render().bytes
        self.assertEqual(res, new_value)

    def test_vanilla(self):
        uut = DynamicInt(self.the_key, self.bf)
        bf_mutations = get_mutation_set(self.bf)
        uut_mutations = get_mutation_set(uut)
        if not any(x in bf_mutations for x in bf_mutations):
            raise AssertionError('Not all similar_mutations are in uut_mutations')
        self.assertGreater(len(uut_mutations), len(bf_mutations))

    def test_not_fuzzable(self):
        uut = DynamicInt(self.the_key, self.bf, fuzzable=False)
        res = uut.render().bytes
        self.assertEqual(res, self.def_value)
        self.assertEqual(uut.num_mutations(), 0)
