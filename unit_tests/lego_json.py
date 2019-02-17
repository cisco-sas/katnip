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

import json
from binascii import hexlify
from katnip.legos import json as kjson
from kitty.model import Template
from kitty.model import String, UInt32
from kitty.model import ENC_INT_DEC

from common import BaseTestCase, get_mutation_set, warp_with_template

test_logger = None


class JsonBooleanTests(BaseTestCase):

    def test_no_value_2_mutations(self):
        '''
        Verify that when no value is set, only two mutations may happen - true and false
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool'))
        self.assertEqual(t.num_mutations(), 2)
        mutations = get_mutation_set(t)
        self.assertEqual(mutations, set([b'true', b'false']))

    def test_value_no_fuzzable_true(self):
        '''
        Verify that the number of mutations is zero when value is set and the field is not fuzzable
        value: True
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool', value=True, fuzzable=False))
        self.assertEqual(t.num_mutations(), 0)
        self.assertEqual(t.mutate(), False)
        self.assertEqual(t.render().bytes.decode(), 'true')

    def test_value_no_fuzzable_false(self):
        '''
        Verify that the number of mutations is zero when value is set and the field is not fuzzable
        value: False
        '''
        t = warp_with_template(kjson.JsonBoolean(name='bool', value=False, fuzzable=False))
        self.assertEqual(t.num_mutations(), 0)
        self.assertEqual(t.mutate(), False)
        self.assertEqual(t.render().bytes.decode(), 'false')

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


class JsonNullTests(BaseTestCase):

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


class JsonStringTests(BaseTestCase):

    def test_valid_string_format(self):
        '''
        Test that a JsonString lego results in a quoted string
        '''
        value = 'kitty'
        t = warp_with_template(kjson.JsonString(name='test', value=value, fuzzable=True))
        res = t.render().bytes.decode()
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
            self.assertEqual(t.render().bytes, b'"%s"' % st.render().bytes)


class JsonObjectTests(BaseTestCase):

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
        t = warp_with_template(
            kjson.JsonObject(
                name='obj1',
                member_dict={
                    'obj2a': kjson.JsonObject(
                        name='obj2a',
                        member_dict={
                            'an_int': UInt32(value=1, encoder=ENC_INT_DEC),
                            'a_string': kjson.JsonString(name='some_name', value='some string')
                        }
                    )
                }
            )
        )
        reference = {
            'obj2a': {
                'an_int': 1,
                'a_string': 'some string',
            }
        }
        rendered = t.render().bytes
        self.logger.debug(rendered)
        result = json.loads(rendered)
        reference = json.loads(json.dumps(reference))
        self.assertEqual(reference, result)

    def test_array_in_object(self):
        '''
        Verify that a JsonArray is encoded properly in a JsonObject
        '''
        t = warp_with_template(
            kjson.JsonObject(
                name='obj1',
                member_dict={
                    'arr': kjson.JsonArray(
                        name='arr',
                        values=[UInt32(value=x, encoder=ENC_INT_DEC) for x in range(0, 10)]
                    )
                }
            )
        )
        reference = {'arr': list(range(0, 10))}
        rendered = t.render().bytes
        self.logger.debug(rendered)
        result = json.loads(rendered)
        reference = json.loads(json.dumps(reference))
        self.assertEqual(reference, result)

    def test_multiple_types_in_object(self):
        '''
        Verify that multiple types are encoded properly in a JsonObject
        '''
        t = warp_with_template(
            kjson.JsonObject(
                name='obj1',
                member_dict={
                    'obj2a': kjson.JsonObject(
                        name='obj2a',
                        member_dict={
                        }
                    ),
                    'an_int': UInt32(value=1, encoder=ENC_INT_DEC),
                    'a_string': kjson.JsonString(name='some_name', value='some string')
                }
            )
        )
        reference = {
            'obj2a': {
            },
            'an_int': 1,
            'a_string': 'some string',
        }
        rendered = t.render().bytes
        self.logger.debug(rendered)
        result = json.loads(rendered)
        reference = json.loads(json.dumps(reference))
        self.assertEqual(reference, result)

    def test_empty_object(self):
        '''
        Verify that an empty object is encoded properly json
        '''
        t = warp_with_template(
            kjson.JsonObject(
                name='obj1',
                member_dict={}
            )
        )
        reference = {}
        rendered = t.render().bytes
        self.logger.debug(rendered)
        result = json.loads(rendered)
        reference = json.loads(json.dumps(reference))
        self.assertEqual(reference, result)


class JsonArrayTests(BaseTestCase):

    def test_ints_in_array(self):
        '''
        Verify that a list of ints is encoded properly in a JsonArray
        '''
        the_list = [1, 5, 2, 1000]
        field_list = [UInt32(x, encoder=ENC_INT_DEC, name='%s' % x) for x in the_list]
        t = warp_with_template(kjson.JsonArray(name='test', values=field_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
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
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
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
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
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
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)

    def test_objects_in_array(self):
        '''
        Verify that a list of JsonObjects is encoded properly in a JsonArray
        '''
        the_list = []
        for i in range(10):
            the_list.append(kjson.JsonObject(name='obj_%d' % i, member_dict={'internal': UInt32(value=i, encoder=ENC_INT_DEC)}, fuzz_keys=False))
        t = warp_with_template(kjson.JsonArray(name='test', values=the_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
        res = json.loads(rendered)
        self.assertEqual(len(res), 10)
        for i in range(10):
            self.assertEqual(res[i]['internal'], i)

    def test_arrays_in_array(self):
        '''
        Verify that a list of JsonArrays is encoded properly in a JsonArray
        '''
        the_list = []
        for i in range(10):
            the_list.append(
                kjson.JsonArray(
                    name='arr_%d' % i,
                    values=[
                        UInt32(value=x, encoder=ENC_INT_DEC) for x in range(i, i + 5)
                    ]))
        t = warp_with_template(kjson.JsonArray(name='test', values=the_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
        res = json.loads(rendered)
        self.assertEqual(len(res), 10)
        for i in range(10):
            self.assertEqual(res[i], list(range(i, i + 5)))

    def test_empty_array(self):
        '''
        Verify that an empty list is encoded properly in a JsonArray
        '''
        the_list = []
        t = warp_with_template(kjson.JsonArray(name='test', values=the_list))
        rendered = t.render().bytes
        self.logger.debug('rendered: %s', rendered)
        self.logger.debug('rendered (hex): %s', hexlify(rendered).decode())
        res = json.loads(rendered)
        for i, j in zip(the_list, res):
            self.assertEqual(i, j)


class ListToJsonArrayTests(BaseTestCase):
    '''
    test the generated json list from :func:`~katnip.legos.json.list_to_JsonArray`
    '''

    def _compare_to_ref(self, ref_list):
        uut = kjson.list_to_JsonArray(the_list=ref_list, name='uut')
        res = json.loads(uut.render().bytes)
        ref = json.loads(json.dumps(ref_list))
        self.assertEqual(res, ref)

    def test_empty_list(self):
        self._compare_to_ref([])

    def test_list_of_empty_lists(self):
        self._compare_to_ref([[], [], []])

    def test_list_ints(self):
        self._compare_to_ref([1, 2, 3])

    def test_list_strings(self):
        self._compare_to_ref(['a', 'b', 'c', 'd'])

    def test_list_of_none(self):
        self._compare_to_ref([None, None, None])

    def test_list_of_booleans(self):
        self._compare_to_ref([True, True, False, True, False, False, True])

    def test_list_of_empty_objects(self):
        self._compare_to_ref([{}, {}, {}])

    def test_list_of_objects(self):
        self._compare_to_ref([{'a': 1, 'b': 2}, {'c': 1, 'a': 2}, {'e': 15, 'v': 3}])

    def test_list_of_various(self):
        self._compare_to_ref([1, None, True, 'blah'])


class DictToJsonObjectTests(BaseTestCase):
    '''
    test the generated json object from :func:`~katnip.legos.json.dict_to_JsonObject`
    '''

    def _compare_to_ref(self, ref_dict):
        uut = kjson.dict_to_JsonObject(the_dict=ref_dict, name='uut')
        res = json.loads(uut.render().bytes)
        ref = json.loads(json.dumps(ref_dict))
        self.assertEqual(res, ref)

    def test_empty_object(self):
        self._compare_to_ref({})

    def test_object_with_int(self):
        self._compare_to_ref({'a': 1})

    def test_object_with_null(self):
        self._compare_to_ref({'a': None})

    def test_object_with_bool_true(self):
        self._compare_to_ref({'a': True})

    def test_object_with_bool_false(self):
        self._compare_to_ref({'a': False})

    def test_object_with_empty_arr(self):
        self._compare_to_ref({'a': []})

    def test_object_with_full_arr(self):
        self._compare_to_ref({'a': [1, 2, 3]})

    def test_object_with_empty_object(self):
        self._compare_to_ref({'a': {}})

    def test_object_with_full_object(self):
        self._compare_to_ref({'a': {'a': 1, 'b': 2}})

    def test_object_of_various(self):
        self._compare_to_ref({
            'int': 123,
            'negative': -123,
            'string': 'baum',
            'null': None,
            'list': [1, 2, 3],
            'obj': {
                'mem1': '1',
                'mem2': 2,
            }
        })


class StrToJson(BaseTestCase):
    '''
    test the generated json object from :func:`~katnip.legos.json.str_to_json`
    '''

    def _compare_to_ref(self, ref_str):
        uut = kjson.str_to_json(ref_str, name='uut')
        res = json.loads(uut.render().bytes)
        ref = json.loads(ref_str)
        self.assertEqual(res, ref)

    def test_empty_object(self):
        self._compare_to_ref('{}')

    def test_object_with_int(self):
        self._compare_to_ref('{"a": 1}')

    def test_object_with_null(self):
        self._compare_to_ref('{"a": null}')

    def test_object_with_bool_true(self):
        self._compare_to_ref('{"a": true}')

    def test_object_with_bool_false(self):
        self._compare_to_ref('{"a": false}')

    def test_object_with_empty_arr(self):
        self._compare_to_ref('{"a": []}')

    def test_object_with_full_arr(self):
        self._compare_to_ref('{"a": [1, 2, 3]}')

    def test_object_with_empty_object(self):
        self._compare_to_ref('{"a": {}}')

    def test_object_with_full_object(self):
        self._compare_to_ref('{"a": {"a": 1, "b": 2}}')

    def test_object_of_various(self):
        self._compare_to_ref('''{
            "int": 123,
            "negative": -123,
            "string": "baum",
            "null": null,
            "list": [1, 2, 3],
            "obj": {
                "mem1": "1",
                "mem2": 2
            },
            "bool": true
        }''')

    def test_empty_list(self):
        self._compare_to_ref('[]')

    def test_list_of_empty_lists(self):
        self._compare_to_ref('[[], [], []]')

    def test_list_ints(self):
        self._compare_to_ref('[1, 2, 3]')

    def test_list_strings(self):
        self._compare_to_ref('["a", "b", "c", "d"]')

    def test_list_of_none(self):
        self._compare_to_ref('[null, null, null]')

    def test_list_of_booleans(self):
        self._compare_to_ref('[true, true, false, true]')

    def test_list_of_empty_objects(self):
        self._compare_to_ref('[{}, {}, {}]')

    def test_list_of_objects(self):
        self._compare_to_ref('[{"a": 1, "b": 2}, {"c": 1, "a": 2}, {"e": 15, "v": 3}]')

    def test_list_of_various(self):
        self._compare_to_ref('[1, null, true, "blah"]')
