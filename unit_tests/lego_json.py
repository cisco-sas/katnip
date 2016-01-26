# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This file is part of Kitty.
#
# Kitty is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Kitty is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kitty.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import logging
import json

from katnip.legos import json as kjson
from kitty.model import Template
from kitty.model import String, UInt32
from kitty.model import ENC_INT_DEC

test_logger = None


def get_test_logger():
    global test_logger
    if test_logger is None:
        logger = logging.getLogger('JSON Legos')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] -> %(message)s'
        )
        handler = logging.FileHandler('logs/test_lego_json.log', mode='w')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        test_logger = logger
    return test_logger


def warp_with_template(json_obj):
    '''
    wrap a lego with template
    '''
    t = Template(name='test template', fields=json_obj)
    return t


def get_mutation_set(t):
    '''
    return a list of all mutations for the template
    '''
    res = set([])
    res.add(t.render().bytes)
    while t.mutate():
        res.add(t.render().bytes)
    return res


class JsonTestCase(unittest.TestCase):

    def setUp(self):
        self.logger = get_test_logger()
        self.logger.info('TESTING METHOD: %s', self._testMethodName)

    def prepare(self):
        pass


class JsonBooleanTests(JsonTestCase):

    def test_no_value_2_mutations(self):
        '''
        Verify that when no value is set, only two mutations may happen - true and false
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool'))
        self.assertEqual(t.num_mutations(), 2)
        mutations = get_mutation_set(t)
        self.assertEqual(mutations, set(['true', 'false']))

    def test_value_no_fuzzable_true(self):
        '''
        Verify that the number of mutations is zero when value is set and the field is not fuzzable
        value: True
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool', value=True, fuzzable=False))
        self.assertEqual(t.num_mutations(), 0)
        self.assertEqual(t.mutate(), False)
        self.assertEqual(t.render().bytes, 'true')

    def test_value_no_fuzzable_false(self):
        '''
        Verify that the number of mutations is zero when value is set and the field is not fuzzable
        value: False
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool', value=False, fuzzable=False))
        self.assertEqual(t.num_mutations(), 0)
        self.assertEqual(t.mutate(), False)
        self.assertEqual(t.render().bytes, 'false')

    def test_exception_value_not_bool(self):
        '''
        Verify that an exception is raise when instantiation JsonBoolean with value that is not of type bool
        '''
        with self.assertRaises(ValueError):
            kjson.JsonBoolean(name='bool', value='true', fuzzable=False)
        with self.assertRaises(ValueError):
            kjson.JsonBoolean(name='bool', value='true', fuzzable=True)
        with self.assertRaises(ValueError):
            kjson.JsonBoolean(name='bool', value=0, fuzzable=False)
        with self.assertRaises(ValueError):
            kjson.JsonBoolean(name='bool', value=0, fuzzable=True)

    def test_value_fuzzable_multiple_mutations(self):
        '''
        Verify that when a value is specified and fuzzable is True, there are multiple mutations
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool', value=False, fuzzable=True))
        self.assertGreater(t.num_mutations(), 10)


class JsonNullTests(JsonTestCase):

    def test_not_fuzzable_num_mutations_zero(self):
        '''
        Verify that the number of mutations is zero when the field is not fuzzable
        '''
        t = warp_with_template(kjson.JsonNull(name='null'))
        self.assertEqual(t.num_mutations(), 0)
        self.assertEqual(t.mutate(), False)

    def test_fuzzable_same_as_string_field_null(self):
        '''
        Verify that the number of mutations is the same as for a StringField with value 'null'
        '''
        t = warp_with_template(kjson.JsonNull(name='null', fuzzable=True))
        st = Template(name='reference template', fields=String('null', name='snull'))
        self.assertEqual(t.num_mutations(), st.num_mutations())
        while t.mutate():
            st.mutate()
            self.assertEqual(t.render().bytes, st.render().bytes)


class JsonStringTests(JsonTestCase):

    def test_valid_string_format(self):
        '''
        Test that a JsonString lego results in a quoted string
        '''
        value = 'kitty'
        t = warp_with_template(kjson.JsonString(name='test', value=value, fuzzable=True))
        res = t.render().bytes
        self.assertEqual(res, '"%s"' % value)

    def test_not_fuzzable_num_mutations_zero(self):
        '''
        Verify that the number of mutations is zero when the field is not fuzzable
        '''
        t = warp_with_template(kjson.JsonString(name='test', value='kitty', fuzzable=False))
        self.assertEqual(t.num_mutations(), 0)
        self.assertEqual(t.mutate(), False)

    def test_fuzzable_same_as_quoted_string_field(self):
        '''
        Verify that the number of mutations is the same as for a quoted StringField with the same default value
        '''
        value = 'kitty'
        t = warp_with_template(kjson.JsonString(name='test', value=value, fuzzable=True))
        st = Template(name='reference template', fields=String(name='reference', value=value))
        self.assertEqual(t.num_mutations(), st.num_mutations())
        while t.mutate():
            st.mutate()
            self.assertEqual(t.render().bytes, '"%s"' % st.render().bytes)


class JsonObjectTests(JsonTestCase):

    def test_int_in_object(self):
        '''
        Verify that an int is encoded properly in a JsonObject
        '''
        member_value, member_key = (123, 'the_int')
        member_field = UInt32(member_value, encoder=ENC_INT_DEC, name='field')
        member_dict = {member_key: member_field}
        t = warp_with_template(kjson.JsonObject(name='test', member_dict=member_dict, fuzz_keys=False))
        rendered = t.render().bytes
        d = json.loads(rendered)
        self.assertEqual(d[member_key], member_value)

    def test_string_in_object(self):
        '''
        Verify that a JsonString is encoded properly in a JsonObject
        '''
        member_value, member_key = ('test string', 'the_string')
        member_field = kjson.JsonString(name='field', value=member_value)
        member_dict = {member_key: member_field}
        t = warp_with_template(kjson.JsonObject(name='test', member_dict=member_dict, fuzz_keys=False))
        rendered = t.render().bytes
        d = json.loads(rendered)
        self.assertEqual(d[member_key], member_value)

    def test_bool_in_object(self):
        '''
        Verify that bool is encoded properly in a JsonObject
        '''
        member_value, member_key = (True, 'the_bool')
        member_field = kjson.JsonBoolean(name='field', value=member_value)
        member_dict = {member_key: member_field}
        t = warp_with_template(kjson.JsonObject(name='test', member_dict=member_dict, fuzz_keys=False))
        rendered = t.render().bytes
        d = json.loads(rendered)
        self.assertEqual(d[member_key], member_value)

    def test_null_in_object(self):
        '''
        Verify that a null is encoded properly in a JsonObject
        '''
        member_value, member_key = (None, 'the_bool')
        member_field = kjson.JsonNull(name='field')
        member_dict = {member_key: member_field}
        t = warp_with_template(kjson.JsonObject(name='test', member_dict=member_dict, fuzz_keys=False))
        rendered = t.render().bytes
        d = json.loads(rendered)
        self.assertEqual(d[member_key], member_value)

    def test_object_in_object(self):
        '''
        Verify that a JsonObject is encoded properly in a JsonObject
        '''
        raise NotImplementedError

    def test_array_in_object(self):
        '''
        Verify that a JsonArray is encoded properly in a JsonObject
        '''
        raise NotImplementedError

    def test_multiple_types_in_object(self):
        '''
        Verify that multiple types are encoded properly in a JsonObject
        '''
        raise NotImplementedError

    def test_empty_object(self):
        '''
        Verify that an empty object is encoded properly json
        '''
        raise NotImplementedError


class JsonArrayTests(JsonTestCase):

    def test_ints_in_array(self):
        '''
        Verify that a list of ints is encoded properly in a JsonArray
        '''
        the_list = [1, 5, 2, 1000]
        field_list = [UInt32(x, encoder=ENC_INT_DEC, name='%s' % x) for x in the_list]
        t = warp_with_template(kjson.JsonArray(name='test', values=field_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', rendered.encode('hex'))
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)

    def test_strings_in_array(self):
        '''
        Verify that a list of JsonStrings is encoded properly in a JsonArray
        '''
        the_list = ['1', 'broom', 'link', 'overflow', 'doritos']
        field_list = [kjson.JsonString(name=x, value=x) for x in the_list]
        t = warp_with_template(kjson.JsonArray(name='test', values=field_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', rendered.encode('hex'))
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)

    def test_bools_in_array(self):
        '''
        Verify that a list of JsonBoolean is encoded properly in a JsonArray
        '''
        the_list = [True, False, True, True, False, False, True]
        field_list = [kjson.JsonBoolean(name='%s_%s' % (x, i), value=x) for i, x in enumerate(the_list)]
        t = warp_with_template(kjson.JsonArray(name='test', values=field_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', rendered.encode('hex'))
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)

    def test_nulls_in_array(self):
        '''
        Verify that a list of JsonNulls is encoded properly in a JsonArray
        '''
        the_list = [None, None, None]
        field_list = [kjson.JsonNull(name='%s' % x) for x in range(len(the_list))]
        t = warp_with_template(kjson.JsonArray(name='test', values=field_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', rendered.encode('hex'))
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)

    def test_objects_in_array(self):
        '''
        Verify that a list of JsonObjects is encoded properly in a JsonArray
        '''
        raise NotImplementedError

    def test_arrays_in_array(self):
        '''
        Verify that a list of JsonArrays is encoded properly in a JsonArray
        '''
        raise NotImplementedError

    def test_empty_array(self):
        '''
        Verify that an empty list is encoded properly in a JsonArray
        '''
        the_list = []
        t = warp_with_template(kjson.JsonArray(name='test', values=the_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', rendered.encode('hex'))
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)


class JsonFuncArrayFromStringTests(JsonTestCase):

    def test_(self):
        raise NotImplementedError
