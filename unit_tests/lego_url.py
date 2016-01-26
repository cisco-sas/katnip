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


class HttpUrlTestCase(UrlTestCase):

    def test_ConstructedUrl(self):
        kurl.HttpUrl(
            'http',
            kurl.HostPort('www.google.com', port=123, name='our host'),
            kurl.Path('index.html', name='the page'),
            kurl.Search('sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8'),
            name='http_test_url'
        )


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
