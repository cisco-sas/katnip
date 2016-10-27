from kitty.model import Container, Static, OneOf, ElementCount
from kitty.model import LE32, SizeInBytes, String, RandomBytes
from kitty.model import ENC_INT_LE
import struct


class apev2item(Container):
    def __init__(self, key, value, flags=0, fuzzable=True):
        fields = [
            SizeInBytes(name="Size of Item Value", sized_field="Item Value", length=32,
                        encoder=ENC_INT_LE),
            LE32(name="Item Flags", value=flags),
            String(name="Item Key", value=key, fuzzable=False),
            Static("\x00"),
            Container(name="Item Value", fields=[value])
        ]
        super(apev2item, self).__init__(name=key, fields=fields, fuzzable=fuzzable)


class apev2textitem(apev2item):
    def __init__(self, key, value, fuzzable=True):
        value_field = String(name="key", value=value)
        super(apev2textitem, self).__init__(key, value_field, flags=0, fuzzable=fuzzable)


apev2container = Container(name="apev2container", fields=[
    Static("APETAGEX"),
    LE32(name="version", value=struct.unpack("<I", "2000")[0]),
    SizeInBytes(name="size", sized_field="items and footer", length=32, encoder=ENC_INT_LE),
    ElementCount(depends_on="items", length=32, name="item count", encoder=ENC_INT_LE),
    LE32(name="flags", value=0xa0000000),
    RandomBytes(name="reserved", value="\x00"*8, min_length=8, max_length=8),
    Container(name="items and footer", fields=[
        OneOf(name="items", fields=[
            apev2textitem("Title", "Music Piece Title"),
            apev2textitem("Subtitle", "Title when TITLE contains the work or additional sub title"),
            apev2textitem("Artist", "Performing artist"),
            apev2textitem("Album", "Album name"),
            apev2textitem("Debut album", "Debut album name"),
            apev2textitem("Publisher", "Record label or publisher"),
            apev2textitem("Conductor", "Conductor"),
            apev2textitem("Track", "1"),
            apev2textitem("Composer", "Name of the original composer"),
            apev2textitem("Comment", "User comments"),
            apev2textitem("Copyright", "Copyright holder"),
            apev2textitem("Publicationright", "Publication right holder"),
            apev2textitem("File", "File location"),
            apev2textitem("EAN", "0123456789123"),
            apev2textitem("UPC", "012345678912"),
            apev2textitem("ISBN", "0123456789"),
            apev2textitem("Catalog", "Catalog number"),
            apev2textitem("LC", "LC01234"),
            apev2textitem("Year", "1980"),
            apev2textitem("Record Date", "1980"),
            apev2textitem("Record Location", "Record location"),
            apev2textitem("Genre", "Genre"),
            apev2textitem("Media", "Source"),
            apev2textitem("Index", "1.1"),
            apev2textitem("Related", "http://localhost:8080/related"),
            apev2textitem("ISRC", "01235"),
            apev2textitem("Abstract", "http://localhost:8080/abstract"),
            apev2textitem("Language", "English"),
            apev2textitem("Bibliography", "http://localhost:8080/bibliography?a=1"),
            apev2textitem("Introplay", "1.1"),
        ]),
    ])
])
