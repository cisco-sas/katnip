import unittest
import logging

from katnip.legos import url as kurl
from kitty.core import KittyException

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


class UrlTestCase(unittest.TestCase):

    def setUp(self):
        self.logger = get_test_logger()
        self.logger.info('TESTING METHOD: %s', self._testMethodName)

    def prepare(self):
        pass


class IpUrlTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


def get_all_mutations(uut):
    res = []
    while uut.mutate():
        res.append(uut.render().bytes)
    uut.reset()
    return res


class LoginTestCase(UrlTestCase):
    '''
    Tests for the URL Login field
    '''

    def test_default_full(self):
        '''
        Verify default rendered value of login with username and password
        '''
        expected = 'user:password@'
        uut = kurl.Login(username='user', password='password')
        actual = uut.render().bytes
        self.assertEqual(actual, expected)

    def test_no_username_with_password(self):
        '''
        Verify that an exception is raised when creating a Login
        without username but with password
        '''
        with self.assertRaises(KittyException):
            kurl.Login(password='password')

    def test_no_password(self):
        '''
        Verify default rendered value of login with username
        '''
        expected = 'user@'
        uut = kurl.Login(username='user')
        actual = uut.render().bytes
        self.assertEqual(actual, expected)

    def test_empty(self):
        expected = ''
        uut = kurl.Login()
        actual = uut.render().bytes
        self.assertEqual(actual, expected)

    def test_fuzz_username_true(self):
        username = 'theusername'
        password = 'pass'
        uut = kurl.Login(username=username, password=password, fuzz_username=True, fuzz_password=False, fuzz_delims=False)
        mutations = get_all_mutations(uut)
        if all(username in mutation for mutation in mutations):
            raise Exception('username always appear')

    def test_fuzz_username_false(self):
        username = 'theusername'
        password = 'pass'
        uut = kurl.Login(username=username, password=password, fuzz_username=False, fuzz_password=True, fuzz_delims=True)
        mutations = get_all_mutations(uut)
        if not all(username in mutation for mutation in mutations):
            raise Exception('username does not always appear')

    def test_fuzz_password_true(self):
        username = 'theusername'
        password = 'pass'
        uut = kurl.Login(username=username, password=password, fuzz_username=False, fuzz_password=True, fuzz_delims=False)
        mutations = get_all_mutations(uut)
        if all(password in mutation for mutation in mutations):
            raise Exception('password always appear')

    def test_fuzz_password_false(self):
        username = 'theusername'
        password = 'pass'
        uut = kurl.Login(username=username, password=password, fuzz_username=True, fuzz_password=False, fuzz_delims=True)
        mutations = get_all_mutations(uut)
        if not all(password in mutation for mutation in mutations):
            raise Exception('password does not always appear')

    def test_fuzz_delims_true(self):
        username = 'theusername'
        password = 'pass'
        delim1 = ':'
        delim2 = '@'
        uut = kurl.Login(username=username, password=password, fuzz_username=False, fuzz_password=False, fuzz_delims=True)
        mutations = get_all_mutations(uut)
        if all(delim1 in mutation for mutation in mutations):
            raise Exception('"%s" always appear' % delim1)
        if all(delim2 in mutation for mutation in mutations):
            raise Exception('"%s" always appear' % delim2)

    def test_fuzz_delims_false(self):
        username = 'theusername'
        password = 'pass'
        delim1 = ':'
        delim2 = '@'
        uut = kurl.Login(username=username, password=password, fuzz_username=True, fuzz_password=True, fuzz_delims=False)
        mutations = get_all_mutations(uut)
        if not all(delim1 in mutation for mutation in mutations):
            raise Exception('"%s" does not always appear' % delim1)
        if not all(delim2 in mutation for mutation in mutations):
            raise Exception('"%s" does not always appear' % delim2)

    def test_not_fuzzable(self):
        uut = kurl.Login(username='user', password='password', fuzzable=False)
        self.assertEqual(uut.num_mutations(), 0)
        self.assertFalse(uut.mutate())


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class DecimalNumberTestCase(UrlTestCase):
    '''
    Test for the URL's DecimalNumber field
    '''

    def test_default_value(self):
        uut = kurl.DecimalNumber(5)
        expected = '5'
        actual = uut.render().bytes
        self.assertEqual(actual, expected)

    def test_performing_string_mutations(self):
        uut = kurl.DecimalNumber(5)
        mutations = get_all_mutations(uut)
        int_cnt = sum(is_int(x) for x in mutations)
        self.assertLess(int_cnt, len(mutations))
        non_int_cnt = sum(not is_int(x) for x in mutations)
        self.assertGreater(non_int_cnt, 5)


class HostPortTestCase(UrlTestCase):
    '''
    Tests for URL HostPort
    '''
    def test_default_full(self):
        expected = 'www.example.com:1234'
        uut = kurl.HostPort('www.example.com', port=1234)
        actual = uut.render().bytes
        self.assertEqual(actual, expected)

    def test_no_port(self):
        expected = 'www.example.com'
        uut = kurl.HostPort('www.example.com')
        actual = uut.render().bytes
        self.assertEqual(actual, expected)

    def test_fuzz_host_true(self):
        host = 'www.example.com'
        port = 1234
        uut = kurl.HostPort(host, port, fuzz_host=True, fuzz_port=False, fuzz_delim=False)
        mutations = get_all_mutations(uut)
        if all(host in mutation for mutation in mutations):
            raise Exception('host always appear')

    def test_fuzz_host_false(self):
        host = 'www.example.com'
        port = 1234
        uut = kurl.HostPort(host, port, fuzz_host=False, fuzz_port=True, fuzz_delim=True)
        mutations = get_all_mutations(uut)
        if not all(host in mutation for mutation in mutations):
            raise Exception('host does not always appear')

    def test_fuzz_port_true(self):
        host = 'www.example.com'
        port = '1234'
        uut = kurl.HostPort(host, int(port), fuzz_host=False, fuzz_port=True, fuzz_delim=False)
        mutations = get_all_mutations(uut)
        if all(port in mutation for mutation in mutations):
            raise Exception('port always appear')

    def test_fuzz_port_false(self):
        host = 'www.example.com'
        port = '1234'
        uut = kurl.HostPort(host, int(port), fuzz_host=True, fuzz_port=False, fuzz_delim=True)
        mutations = get_all_mutations(uut)
        if not all(port in mutation for mutation in mutations):
            raise Exception('port does not always appear')

    def test_fuzz_delim_true(self):
        host = 'www.example.com'
        port = '1234'
        delim = ':'
        uut = kurl.HostPort(host, int(port), fuzz_host=False, fuzz_port=False, fuzz_delim=True)
        mutations = get_all_mutations(uut)
        if all(delim in mutation for mutation in mutations):
            raise Exception('delim always appear')

    def test_fuzz_delim_false(self):
        host = 'www.example.com'
        port = '1234'
        delim = ':'
        uut = kurl.HostPort(host, int(port), fuzz_host=True, fuzz_port=True, fuzz_delim=False)
        mutations = get_all_mutations(uut)
        if not all(delim in mutation for mutation in mutations):
            raise Exception('delim does not always appear')


class HostNameTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class SearchTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class PathTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class FTypeTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class FtpUrlTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class EmailAddressTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class EmailUrlTestCase(UrlTestCase):
    def test_not_implemented(self):
        raise NotImplemented


class HttpUrlTestCase(UrlTestCase):

    def test_constructed_url_full(self):
        '''
        verify the default value of a url without login
        '''
        expected = 'http://user:pass@www.google.com:123/index.html?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8'
        container = kurl.HttpUrl(
            'http',
            login=kurl.Login('user', 'pass'),
            hostport=kurl.HostPort('www.google.com', port=123, name='our host'),
            path=kurl.Path('index.html', name='the page'),
            search=kurl.Search('sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8'),
            name='uut'
        )
        actual = container.render().bytes
        self.assertEqual(actual, expected)

    def test_constructed_url_no_login(self):
        '''
        verify the default value of a url without login
        '''
        expected = 'http://www.google.com:123/index.html?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8'
        container = kurl.HttpUrl(
            'http',
            hostport=kurl.HostPort('www.google.com', port=123, name='our host'),
            path=kurl.Path('index.html', name='the page'),
            search=kurl.Search('sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8'),
            name='uut'
        )
        actual = container.render().bytes
        self.assertEqual(actual, expected)

    def test_constructed_url_no_search(self):
        '''
        verify the default value of a url without serach (query) field
        '''
        expected = 'http://www.google.com:123/index.html'
        container = kurl.HttpUrl(
            'http',
            hostport=kurl.HostPort('www.google.com', port=123, name='our host'),
            path=kurl.Path('index.html', name='the page'),
            name='uut'
        )
        actual = container.render().bytes
        self.assertEqual(actual, expected)

    def test_constructed_url_no_path(self):
        '''
        verify the default value of a url without serach (query) field
        '''
        expected = 'http://www.google.com:123'
        container = kurl.HttpUrl(
            'http',
            hostport=kurl.HostPort('www.google.com', port=123, name='our host'),
            name='uut'
        )
        actual = container.render().bytes
        self.assertEqual(actual, expected)


class FromStringTests(UrlTestCase):

    def _test_vanilla_supported(self, url, expected_class):
        container = kurl.url_from_string(url)
        self.assertEqual(type(container), expected_class)
        rendered = container.render().tobytes()
        self.assertEqual(url, rendered)

    def test_supported_ftp(self):
        self._test_vanilla_supported('ftp://usr:pass@some.server.com', kurl.FtpUrl)

    def test_supported_ftps(self):
        self._test_vanilla_supported('ftps://usr:pass@some.server.com', kurl.FtpUrl)

    def test_supported_http(self):
        self._test_vanilla_supported('http://usr:pass@some.server.com/and/some/path', kurl.HttpUrl)

    def test_supported_https(self):
        self._test_vanilla_supported('https://usr:pass@some.server.com/and/some/path', kurl.HttpUrl)

    def test_supported_mailto(self):
        self._test_vanilla_supported('mailto:test@gmail.com', kurl.EmailUrl)

    def _test_unsupported_exception(self, url):
        with self.assertRaises(KittyException):
            kurl.url_from_string(url)

    def test_unsupported_no_scheme(self):
        '''
        No scheme
        '''
        self._test_unsupported_exception('www.google.com')

    def test_unsupported_scheme(self):
        self._test_unsupported_exception('file:///etc/passwd')
