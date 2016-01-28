import unittest
import logging

from katnip.legos.dynamic import DynamicExtended, DynamicInt, DynamicString
from kitty.model import Template
from kitty.model import String
from kitty.model import BE32
from kitty.model import ENC_INT_DEC, ENC_STR_BASE64_NO_NL


test_logger = None


def get_test_logger():
    global test_logger
    if test_logger is None:
        logger = logging.getLogger('DynamicExtended Legos')
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
    t.reset()
    return res


class DynamicTestCase(unittest.TestCase):

    def setUp(self):
        self.logger = get_test_logger()
        self.logger.info('TESTING METHOD: %s', self._testMethodName)
        self.def_value = '1234'
        self.the_key = 'the_key'

    def prepare(self):
        pass


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
        similar_string = String(self.def_value, encoder=ENC_STR_BASE64_NO_NL)
        uut = DynamicString(key=self.the_key, value=self.def_value, encoder=ENC_STR_BASE64_NO_NL)
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
