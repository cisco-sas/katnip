from kitty.model import Template, Container, Static, OneOf
from id3v23 import id3v23container
from apetagv2 import apev2container

mp3base = Template(name="mp3base", fields=[
    OneOf(name="tag", fields=[
        id3v23container,
        apev2container
    ]),
    Container(name="audio_frame", fields=[
        Static(name="default_data",
               value="fff310c40002d11aec01401001fffffffffa9c0c0c0c0cf9d5fffff312c40103593f1401803800ffffffd3ff512097c1f37a81aa27fff310c40102f91ee809c08000fffffffff288b841789e3f0008fff310c40202f91b007800143e0403f5fffff0a809cd56000c07fff310c403036916ec7800612003f3ffffea082126016d4d000cfff310c40203291f1c78000e3f0703f5fffff106507aaee2000afff310c40202e1170c7800143f0503f5fffff0606980fa000e07fff310c40302e803307800447203fffffb7fea702755000e0703fff310c40402a123307800872af5fffff8d19ea50281fffffffffff312c40602a11f2819401002fe71a21c85fffffffffff3140dfcfff310c40903493f1401803801207f424a2afffffffc1a51e416fff310c408028006d801c000000e164c414d45332e3937202861fff310c40b00000348000000006c70686129aaaaaaaaaaaaaaaa".decode("hex")),
    ])
])
