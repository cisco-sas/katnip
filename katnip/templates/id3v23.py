from kitty.model import Template, Container, Static, OneOf, Repeat
from kitty.model import BE8, BE16, BE32, SizeInBytes, String, BaseField, RandomBytes
from kitty.model import BitFieldBinEncoder, ENC_INT_BE, StrNullTerminatedEncoder
from bitstring import Bits
import struct


STR_ENC_NULLTERM = StrNullTerminatedEncoder()


class id3v23_size_encoder(BitFieldBinEncoder):
    def __init__(self):
        super(id3v23_size_encoder, self).__init__("be")

    def encode(self, value, length, signed):
        bs = "".join(chr((value >> 7 * (3 - i)) & 0x7f) for i in range(4))
        return Bits(bytes=bs)


class id3v23_frame(Container):
    def __init__(self, frameid, fields, flags=0, fuzzable=True,
                 fuzz_frame_id=False):
        content = Container(name="content", fields=fields)
        header = Container(name="header", fields=[
            BE32(name="Frame ID", value=struct.unpack(">I", frameid)[0],
                 fuzzable=fuzz_frame_id),
            SizeInBytes(name="Size", sized_field=content, length=32, encoder=ENC_INT_BE),
            BE16(name="Flags", value=flags),
        ])
        fields = [header, content]

        super(id3v23_frame, self).__init__(name=frameid, fields=fields, fuzzable=fuzzable)


class id3v23_text_frame(id3v23_frame):
    def __init__(self, frameid, value, flags=0, encoding=0, fuzzable=True,
                 fuzz_frame_id=False):
        if isinstance(value, BaseField):
            field = value
        else:
            field = String(name="value", value=value, encoder=STR_ENC_NULLTERM)

        fields = [
            BE8(name="encoding", value=encoding),
            field
        ]
        super(id3v23_text_frame, self).__init__(frameid, flags=flags, fields=fields,
                                                fuzzable=fuzzable,
                                                fuzz_frame_id=fuzz_frame_id)


class id3v23_url_frame(id3v23_frame):
    def __init__(self, frameid, flags=0, name=None, fuzzable=True,
                 fuzz_frame_id=False):
        fields = [
            String(name="url", value="http://127.0.0.1:8080/{0}?a=1&b=2".format(frameid))
        ]
        super(id3v23_url_frame, self).__init__(frameid, flags=flags, fields=fields,
                                               fuzzable=fuzzable,
                                               fuzz_frame_id=fuzz_frame_id)


id3v23container = Container(name="id3v23container", fields=[
    Static("ID3"),
    BE8(name="majorversion", value=3),
    BE8(name="revision", value=0),
    BE8(name="flags", value=0x00, fuzzable=False),
    SizeInBytes(name="size", sized_field="frames", length=28,
                encoder=id3v23_size_encoder()),
    # TODO: Extended header
    OneOf(name="frames", fields=[

        id3v23_frame("UFID", fields=[
            String(name="Owner Identifier", value="owner identifier",
                   encoder=STR_ENC_NULLTERM),
            RandomBytes(name="Identifier", value="A"*64, min_length=1, max_length=100)
        ]),
        id3v23_text_frame("TALB", value="Album/Movie/Show title"),
        id3v23_text_frame("TBPM", value="100"),  # TODO: numeric strings only
        id3v23_text_frame("TCOM", value="Composer"),
        id3v23_text_frame("TCON", value="(0)Hard rock"),  # TODO: implement encoding
        id3v23_text_frame("TCOP", value="Copyright message"),
        id3v23_text_frame("TDAT", value="2609"),
        id3v23_text_frame("TDLY", value="100"),  # TODO: numeric strings only?
        id3v23_text_frame("TENC", value="Encoded by"),
        id3v23_text_frame("TEXT", value="Lyricist/Text writer"),
        id3v23_text_frame("TFLT", value="MPG/3"),  # TODO: limit to acceptable values only?
        id3v23_text_frame("TIME", value="0130"),  # TODO: numeric strings only?
        id3v23_text_frame("TIT1", value="Content group description"),
        id3v23_text_frame("TIT2", value="Title/Songname description"),
        id3v23_text_frame("TIT3", value="Subtitle/Description refinement"),
        id3v23_text_frame("TKEY", value="Cbm"),  # TODO: limit to acceptable values only?
        id3v23_text_frame("TLAN", value="eng"),  # TODO: limit to acceptable language values?
        id3v23_text_frame("TLEN", value="100000"),  # TODO: numeric strings only?
        id3v23_text_frame("TMED", value="CD/A"),  # TODO: limit to acceptable values only?
        id3v23_text_frame("TOAL", value="Original album/movie/show title"),
        id3v23_text_frame("TOFN", value="Original_filename.mp3"),
        id3v23_text_frame("TOPE", value="Original artist/performer"),
        id3v23_text_frame("TORY", value="1969"),  # TODO: limit to years
        id3v23_text_frame("TOWN", value="File owner/licensee"),
        id3v23_text_frame("TPE1", value="Lead artist/Lead performer/Soloist/Performing group"),
        id3v23_text_frame("TPE2", value="Band/Orchestra/Accompaniment"),
        id3v23_text_frame("TPE3", value="Conductor"),
        id3v23_text_frame("TPE4", value="Interpreted, remixed, or otherwise modified by"),
        id3v23_text_frame("TPOS", value="1/2"),  # TODO: limit to acceptable values
        id3v23_text_frame("TPUB", value="Publisher"),
        id3v23_text_frame("TRCK", value="1/2"),  # TODO: limit to acceptable values
        id3v23_text_frame("TRDA", value="1st January"),
        id3v23_text_frame("TRSN", value="Internet radio station name"),
        id3v23_text_frame("TRSO", value="Internet radio station owner"),
        id3v23_text_frame("TSIZ", value="340"),  # TODO: numeric only, should match actual file size
        id3v23_text_frame("TSRC", value="USABC6900001"),  # TODO: limit to acceptable values
        id3v23_text_frame("TSSE", value="Software/Hardware and settings used for encoding"),
        id3v23_text_frame("TYER", value="1969"),  # TODO: limit to years
        id3v23_text_frame("TXXX", value=Container(fields=[
            String(name="Description", value="Description", encoder=STR_ENC_NULLTERM),
            String(name="Value", value="Value"),
        ])),
        id3v23_url_frame("WCOM"),
        id3v23_url_frame("WCOP"),
        id3v23_url_frame("WOAF"),
        id3v23_url_frame("WOAR"),
        id3v23_url_frame("WOAS"),
        id3v23_url_frame("WORS"),
        id3v23_url_frame("WPAY"),
        id3v23_url_frame("WPUB"),
        id3v23_text_frame("WXXX", value=Container(fields=[
            String(name="Description", value="Description", encoder=STR_ENC_NULLTERM),
            String(name="URL", value="http://127.0.0.1:8080/WXXX?a=1&b=2")
        ])),
        id3v23_text_frame("IPLS", value=Repeat(min_times=1, max_times=100, step=15, fields=[
            String(name="Involvement", value="Involvement",
                   encoder=STR_ENC_NULLTERM),
            String(name="Involvee", value="Involvee",
                   encoder=STR_ENC_NULLTERM)
        ])),
        # TODO: implement MCDI
        # TODO: implement ETCO
        # TODO: implement MLLT
        # TODO: implement SYTC
        # TODO: implement USLT
        # TODO: implement SYLT
        id3v23_text_frame("COMM", value=Container(fields=[
            String(name="Language", value="eng", fuzzable=False),
            String(name="Short content descrip", value="Short content descrip",
                   encoder=STR_ENC_NULLTERM),
            String(name="Actual text", value="Actual text")
        ])),
        # TODO: implement RVAD
        # TODO: implement EQU
        # TODO: implement RVRB
        id3v23_text_frame("APIC", value=Container(fields=[
            String(name="MIME type", value="image/png", encoder=STR_ENC_NULLTERM),
            BE8(name="Picture type", value=0x03),
            String(name="Description", value="Description", encoder=STR_ENC_NULLTERM),
            Static(name="Picture data",
                   value="89504e470d0a1a0a0000000d4948445200000001000000010100000000376ef9240000001049444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082".decode("hex")),
        ])),
        # TODO: implement GEOB
        id3v23_frame("PCNT", fields=Container(fields=[
            BE32(name="Counter", value=0x1),  # TODO: implement the 'all-ones, add a byte' encoding
        ])),
        id3v23_frame("POPM", fields=Container(fields=[
            String(name="Email to user", value="someone@somedomain.com",
                   encoder=STR_ENC_NULLTERM),
            BE8(name="Rating", value=0x01),
            BE32(name="Counter", value=0x1),  # TODO: implement the 'all-ones, add a byte' encoding
        ])),
        # TODO: implement RBUF
        id3v23_frame("AENC", fields=Container(fields=[
            String(name="Owner identifier", value="Owner identifier",
                   encoder=STR_ENC_NULLTERM),
            BE16(name="Preview start", value=0x0000),
            BE16(name="Preview end", value=0x0000),
            RandomBytes(name="Encryption info", value="A"*64, min_length=1, max_length=100)
        ])),
        # TODO: implement LINK
        # TODO: implement POSS
        id3v23_text_frame("USER", value=Container(fields=[
            String(name="Language", value="eng", fuzzable=False),
            String(name="Actual text", value="actual text"),
        ])),
        id3v23_text_frame("OWNE", value=Container(fields=[
            String(name="Price payed", value="USD1.5", encoder=STR_ENC_NULLTERM),
            String(name="Date of purch", value="20150101"),
            String(name="Seller", value="Seller"),
        ])),
        id3v23_text_frame("COMR", value=Container(fields=[
            String(name="Price string", value="USD1.5", encoder=STR_ENC_NULLTERM),
            String(name="Valid until", value="20150101"),
            String(name="Contact URL", value="http://localhost:8080", encoder=STR_ENC_NULLTERM),
            BE8(name="Received as", value=0x01),
            String(name="Name of seller", value="Name of seller", encoder=STR_ENC_NULLTERM),
            String(name="Description", value="Description", encoder=STR_ENC_NULLTERM),
            String(name="Picture MIME type", value="image/png", encoder=STR_ENC_NULLTERM),
            Static(name="Seller logo",
                   value="89504e470d0a1a0a0000000d4948445200000001000000010100000000376ef9240000001049444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082".decode("hex")),
        ])),
        id3v23_frame("ENCR", fields=Container(fields=[
            String(name="Owner identifier", value="Owner identifier",
                   encoder=STR_ENC_NULLTERM),
            BE8(name="Method symbol", value=0x01),
            RandomBytes(name="Encryption data", value="A"*64, min_length=1, max_length=100),
        ])),
        id3v23_frame("GRID", fields=Container(fields=[
            String(name="Owner identifier", value="Owner identifier",
                   encoder=STR_ENC_NULLTERM),
            BE8(name="Group symbol", value=0x01),
            RandomBytes(name="Group dependent data", value="A"*64, min_length=1, max_length=100),
        ])),
        id3v23_frame("PRIV", fields=Container(fields=[
            String(name="Owner identifier", value="Owner identifier",
                   encoder=STR_ENC_NULLTERM),
            RandomBytes(name="The private data", value="A"*64, min_length=1, max_length=100),
        ])),

    ])
])


mp3base = Template(name="mp3base", fields=[
    OneOf(name="tag", fields=[
        id3v23container
    ]),
    Container(name="audio_frame", fields=[
        Static(name="default_data",
               value="fff310c40002d11aec01401001fffffffffa9c0c0c0c0cf9d5fffff312c40103593f1401803800ffffffd3ff512097c1f37a81aa27fff310c40102f91ee809c08000fffffffff288b841789e3f0008fff310c40202f91b007800143e0403f5fffff0a809cd56000c07fff310c403036916ec7800612003f3ffffea082126016d4d000cfff310c40203291f1c78000e3f0703f5fffff106507aaee2000afff310c40202e1170c7800143f0503f5fffff0606980fa000e07fff310c40302e803307800447203fffffb7fea702755000e0703fff310c40402a123307800872af5fffff8d19ea50281fffffffffff312c40602a11f2819401002fe71a21c85fffffffffff3140dfcfff310c40903493f1401803801207f424a2afffffffc1a51e416fff310c408028006d801c000000e164c414d45332e3937202861fff310c40b00000348000000006c70686129aaaaaaaaaaaaaaaa".decode("hex")),
    ])
])
