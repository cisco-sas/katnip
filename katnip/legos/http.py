from katnip.legos.url import DecimalNumber, Search, Path, urlparse
from kitty.model import Container
from kitty.model import String, Static, Group, Delimiter, Float
from kitty.model import ENC_BITS_BASE64


def _valuename(txt):
    return '%s_value' % txt


def _keyname(txt):
    return '%s_key' % txt


class CustomHeaderField(Container):
    def __init__(self, key, value, end=False, fuzzable_key=False, fuzzable_value=True):
        fields = [
            String(name=_keyname(key), value=key, fuzzable=fuzzable_key),
            Static(': '),
            Container(name=_valuename(key), fields=value, fuzable=fuzzable_value),
            Static('\r\n')
        ]
        if end:
            fields.append(Static('\r\n'))
        super(CustomHeaderField, self).__init__(name=key, fields=fields, fuzzable=fuzzable_value)


class TextField(CustomHeaderField):
    def __init__(self, key, value, end=False, fuzzable_key=False, fuzzable_value=True):
        value_field = [String(name="value", value=value)]
        super(TextField, self).__init__(key, value_field, end, fuzzable_key, fuzzable_value)


class IntField(CustomHeaderField):
    def __init__(self, key, value, end=False, fuzzable_key=False, fuzzable_value=True):
        value_field = [DecimalNumber(
            name="value",
            value=value,
            num_bits=32,
            signed=True
        )]
        super(IntField, self).__init__(key, value_field, end, fuzzable_key, fuzzable_value)


class AuthorizationField(CustomHeaderField):
    def __init__(self, key, username, password, end=False, delim=':', fuzz_username=True, fuzz_password=True, fuzzable_key=False, fuzzable=True):
        value_field = [
            Static('Basic '),
            Container(name='base64_auth', fields=[
                String(name='username', value=username, fuzzable=fuzz_username),
                Delimiter(delim, fuzzable=False),
                String(name='password', value=password, fuzzable=fuzz_password),
            ], encoder=ENC_BITS_BASE64)
        ]
        super(AuthorizationField, self).__init__(key, value_field, end, fuzzable_key, fuzzable)


class HttpRequestLine(Container):
    def __init__(self, method='GET', uri='/', protocol='HTTP', version=1.0, fuzzable_method=False, fuzzable_uri=False, fuzzable=True):
        method_value = [method] if isinstance(method, str) else method
        parsed = urlparse(uri)
        uri_value = [Path(parsed.path, name='path', fuzz_delims=False)]
        if parsed.query:
            uri_value.append(Search(parsed.query, name='search', fuzz_value=True))
        fields = [
            Group(name='method', values=method_value, fuzzable=fuzzable_method),
            Static(' '),
            Container(name='uri', fields=uri_value, fuzzable=fuzzable_uri),
            Static(' '),
            String(name='protocol', value=protocol, fuzzable=False),
            Float(name='version', value=version),
            Static('\r\n'),
        ]
        super(HttpRequestLine, self).__init__(name='http url', fields=fields, fuzzable=fuzzable)
