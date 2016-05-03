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

'''
Tests for low level fields:
'''

from common import metaTest, BaseTestCase
from bitstring import Bits
import types
from kitty.core import KittyException



class ValueTestCase(BaseTestCase):

    __meta__ = True
    default_value = None
    default_value_rendered = None

    def setUp(self, cls=None):
        super(ValueTestCase, self).setUp(cls)
        self.default_value_rendered = self.__class__.default_value_rendered
        self.default_value = self.__class__.default_value
        self.rendered_type = self.get_rendered_type()
        self.uut_name = 'uut'

    def get_rendered_type(self):
        return Bits

    def get_default_field(self, fuzzable=True):
        return self.cls(value=self.default_value, fuzzable=fuzzable, name=self.uut_name)

    def bits_to_value(self, bits):
        '''
        default behavior: take the bytes
        '''
        return bits.bytes

    def _get_all_mutations(self, field, reset=True):
        res = []
        while field.mutate():
            res.append(field.render())
        if reset:
            field.reset()
        return res

    def _base_check(self, field):
        num_mutations = field.num_mutations()
        mutations = self._get_all_mutations(field)
        self.assertEqual(num_mutations, len(mutations))
        self.assertEqual(len(mutations), len(set(mutations)))
        mutations = self._get_all_mutations(field)
        self.assertEqual(num_mutations, len(mutations))
        self.assertEqual(len(mutations), len(set(mutations)))

    @metaTest
    def testDummyToDo(self):
        self.assertEqual(len(self.todo), 0)

    @metaTest
    def testDefaultValue(self):
        field = self.get_default_field()
        res = field.render()
        self.assertEqual(self.default_value_rendered, res)
        field.mutate()
        field.reset()
        res = field.render()
        self.assertEqual(self.default_value_rendered, res)

    @metaTest
    def testMutateAllDifferent(self):
        field = self.get_default_field()
        mutations = self._get_all_mutations(field)
        self.assertEqual(len(set(mutations)), len(mutations))

    @metaTest
    def testNotFuzzable(self):
        field = self.get_default_field(fuzzable=False)
        num_mutations = field.num_mutations()
        self.assertEqual(num_mutations, 0)
        rendered = field.render()
        as_val = self.bits_to_value(rendered)
        self.assertEqual(as_val, self.default_value)
        mutated = field.mutate()
        self.assertFalse(mutated)
        rendered = field.render()
        as_val = self.bits_to_value(rendered)
        self.assertEqual(as_val, self.default_value)
        field.reset()
        mutated = field.mutate()
        self.assertFalse(mutated)
        rendered = field.render()
        as_val = self.bits_to_value(rendered)
        self.assertEqual(as_val, self.default_value)

    @metaTest
    def testNumMutations(self):
        field = self.get_default_field()
        num_mutations = field.num_mutations()
        self._check_mutation_count(field, num_mutations)

    @metaTest
    def testSameResultWhenSameParams(self):
        field1 = self.get_default_field()
        field2 = self.get_default_field()
        res1 = self._get_all_mutations(field1)
        res2 = self._get_all_mutations(field2)
        self.assertListEqual(res1, res2)

    @metaTest
    def testSameResultAfterReset(self):
        field = self.get_default_field()
        res1 = self._get_all_mutations(field)
        res2 = self._get_all_mutations(field)
        self.assertListEqual(res1, res2)

    @metaTest
    def testSkipZero(self):
        field = self.get_default_field(fuzzable=True)
        num_mutations = field.num_mutations()
        to_skip = 0
        expected_skipped = min(to_skip, num_mutations)
        expected_mutated = num_mutations - expected_skipped
        self._check_skip(field, to_skip, expected_skipped, expected_mutated)

    @metaTest
    def testSkipOne(self):
        field = self.get_default_field(fuzzable=True)
        num_mutations = field.num_mutations()
        to_skip = 1
        expected_skipped = min(to_skip, num_mutations)
        expected_mutated = num_mutations - expected_skipped
        self._check_skip(field, to_skip, expected_skipped, expected_mutated)

    @metaTest
    def testSkipHalf(self):
        field = self.get_default_field(fuzzable=True)
        num_mutations = field.num_mutations()
        to_skip = num_mutations / 2
        expected_skipped = min(to_skip, num_mutations)
        expected_mutated = num_mutations - expected_skipped
        self._check_skip(field, to_skip, expected_skipped, expected_mutated)

    @metaTest
    def testSkipExact(self):
        field = self.get_default_field(fuzzable=True)
        num_mutations = field.num_mutations()
        to_skip = num_mutations
        expected_skipped = min(to_skip, num_mutations)
        expected_mutated = num_mutations - expected_skipped
        self._check_skip(field, to_skip, expected_skipped, expected_mutated)

    @metaTest
    def testSkipTooMuch(self):
        field = self.get_default_field(fuzzable=True)
        num_mutations = field.num_mutations()
        to_skip = num_mutations + 1
        expected_skipped = min(to_skip, num_mutations)
        expected_mutated = num_mutations - expected_skipped
        self._check_skip(field, to_skip, expected_skipped, expected_mutated)

    @metaTest
    def testReturnTypeRenderFuzzable(self):
        field = self.get_default_field(fuzzable=True)
        self.assertIsInstance(field.render(), self.rendered_type)
        field.mutate()
        self.assertIsInstance(field.render(), self.rendered_type)
        field.reset()
        self.assertIsInstance(field.render(), self.rendered_type)

    @metaTest
    def testReturnTypeGetRenderedFuzzable(self):
        field = self.get_default_field(fuzzable=True)
        self.assertIsInstance(field.render(), self.rendered_type)
        field.mutate()
        self.assertIsInstance(field.render(), self.rendered_type)
        field.reset()
        self.assertIsInstance(field.render(), self.rendered_type)

    @metaTest
    def testReturnTypeMutateFuzzable(self):
        field = self.get_default_field(fuzzable=True)
        self.assertIsInstance(field.mutate(), types.BooleanType)
        field.reset()
        self.assertIsInstance(field.mutate(), types.BooleanType)

    @metaTest
    def testReturnTypeRenderNotFuzzable(self):
        field = self.get_default_field(fuzzable=False)
        self.assertIsInstance(field.render(), self.rendered_type)
        field.mutate()
        self.assertIsInstance(field.render(), self.rendered_type)
        field.reset()
        self.assertIsInstance(field.render(), self.rendered_type)

    @metaTest
    def testReturnTypeGetRenderedNotFuzzable(self):
        field = self.get_default_field(fuzzable=False)
        self.assertIsInstance(field.render(), self.rendered_type)
        field.mutate()
        self.assertIsInstance(field.render(), self.rendered_type)
        field.reset()
        self.assertIsInstance(field.render(), self.rendered_type)

    @metaTest
    def testReturnTypeMutateNotFuzzable(self):
        field = self.get_default_field(fuzzable=False)
        self.assertIsInstance(field.mutate(), types.BooleanType)
        field.reset()
        self.assertIsInstance(field.mutate(), types.BooleanType)

    @metaTest
    def testHashTheSameForTwoSimilarObjects(self):
        field1 = self.get_default_field()
        field2 = self.get_default_field()
        self.assertEqual(field1.hash(), field2.hash())

    @metaTest
    def testHashTheSameAfterReset(self):
        field = self.get_default_field()
        hash_after_creation = field.hash()
        field.mutate()
        hash_after_mutate = field.hash()
        self.assertEqual(hash_after_creation, hash_after_mutate)
        field.reset()
        hash_after_reset = field.hash()
        self.assertEqual(hash_after_creation, hash_after_reset)
        while field.mutate():
            hash_after_mutate_all = field.hash()
            self.assertEqual(hash_after_creation, hash_after_mutate_all)
            field.render()
            hash_after_render_all = field.hash()
            self.assertEqual(hash_after_creation, hash_after_render_all)

    @metaTest
    def testGetRenderedFields(self):
        field = self.get_default_field()
        field_list = [field]
        self.assertEqual(field.get_rendered_fields(), field_list)
        while field.mutate():
            if len(field.render()):
                self.assertEqual(field.get_rendered_fields(), field_list)
            else:
                self.assertEqual(field.get_rendered_fields(), [])

    @metaTest
    def testInvalidFieldNameRaisesException(self):
        with self.assertRaises(KittyException):
            self.uut_name = 'invalid/name'
            self.get_default_field()

    def _check_skip(self, field, to_skip, expected_skipped, expected_mutated):
        # print('_check_skip(%s, %s, %s, %s)' % (field, to_skip, expected_skipped, expected_mutated))
        skipped = field.skip(to_skip)
        self.assertEqual(expected_skipped, skipped)
        mutated = 0
        while field.mutate():
            mutated += 1
        self.assertEqual(expected_mutated, mutated)
        field.reset()
        skipped = field.skip(to_skip)
        self.assertEqual(expected_skipped, skipped)
        mutated = 0
        while field.mutate():
            mutated += 1
        self.assertEqual(expected_mutated, mutated)

    def _check_mutation_count(self, field, expected_num_mutations):
        num_mutations = field.num_mutations()
        self.assertEqual(num_mutations, expected_num_mutations)
        mutation_count = 0
        while field.mutate():
            mutation_count += 1
        self.assertEqual(mutation_count, expected_num_mutations)
