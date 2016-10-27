from kitty.model import Template, Container, Static, SizeInBytes, ElementCount, List
from kitty.model import String, BE16, BE8, BE32, BitField
from kitty.model import AbsoluteOffset
from kitty.model import ENC_INT_BE, StrNullTerminatedEncoder


STR_ENC_NULLTERM = StrNullTerminatedEncoder()

class Mp4Box(Container):
    def __init__(self, name, fields, fuzzable=True):
        header = Container(name="header", fields=[
            SizeInBytes(name="length", sized_field=self, length=32, encoder=ENC_INT_BE),
            String(name="name", value=name, fuzzable=False)
        ])
        content = Container(name="content", fields=fields)
        super(Mp4Box, self).__init__(name=name.replace("\xa9", "\\xa9"), fields=[header, content],
                                      fuzzable=fuzzable)


class Mp4FullBox(Mp4Box):
    def __init__(self, name, version=0x00, flags=0x0000000, fields=[], fuzzable=True):
        super(Mp4FullBox, self).__init__(name, fields=[
            BE8(name="version", value=version),
            BitField(name="flags", value=flags, length=24, encoder=ENC_INT_BE),
        ] + fields, fuzzable=fuzzable)


class Mp4MetadataBox(Mp4Box):
    def __init__(self, name, type_code=0, fields=None, fuzzable=True):
        super(Mp4MetadataBox, self).__init__(name, fields=[
            Mp4Box("data", fuzzable=fuzzable, fields=[
                BE16(name="typeReserved", value=0),
                BE8(name="typeSetIdentifier", value=0),
                BE8(name="typeCode", value=type_code),
                BE32(name="locale", value=0),
                Container(name="metadata", fields=fields)
            ])
        ])


class Mp4MetadataUtf8Box(Mp4MetadataBox):
    def __init__(self, name, text, fuzzable=True):
        super(Mp4MetadataUtf8Box, self).__init__(name, type_code=1, fields=[
            String(name="text", value=text)
        ], fuzzable=fuzzable)

class HdlrBox(Mp4FullBox):
    def __init__(self, handler_type, component_name, fuzzable=True):
        super(HdlrBox, self).__init__("hdlr", fields=[
            String(name="predefined", value="\x00\x00\x00\x00", fuzzable=False),
            String(name="handler_type", value=handler_type, fuzzable=False),
            String(name="manufacturer", value="appl", fuzzable=False),
            BE32(name="component_flags", value=0x00000000),
            BE32(name="component_mask", value=0x00000000),
            String(name="component_name", value=component_name,
                   encoder=STR_ENC_NULLTERM),
        ], fuzzable=fuzzable)


class TimeToSampleEntry(Container):
    def __init__(self, sample_count, sample_delta, fuzzable=True):
        super(TimeToSampleEntry, self).__init__(fields=[
            BE32(name="sample_count", value=sample_count),
            BE32(name="sample_delta", value=sample_delta)
        ], fuzzable=fuzzable)


class AudioSampleEntry(Mp4Box):
    def __init__(self, name, data_reference_index, channelcount, samplesize,
                 pre_defined, samplerate, fields=[], fuzzable=True):
        super(AudioSampleEntry, self).__init__(name=name, fields=[
            Static(name="reserved0", value="\x00"*6),
            BE16(name="data_reference_index", value=data_reference_index),
            Static(name="reserved1", value="\x00\x00\x00\x00"*2),
            BE16(name="channelcount", value=channelcount),
            BE16(name="samplesize", value=samplesize),
            BE16(name="pre_defined", value=pre_defined),
            BE16(name="reserved2", value=0x0000),
            BE32(name="samplerate", value=samplerate),
        ] + fields, fuzzable=fuzzable)


class SampleToChunkEntry(Container):
    def __init__(self, first_chunk, samples_per_chunk, sample_description_index, fuzzable=True):
        super(SampleToChunkEntry, self).__init__(fields=[
            BE32(name="first_chunk", value=first_chunk),
            BE32(name="samples_per_chunk", value=samples_per_chunk),
            BE32(name="sample_description_index", value=sample_description_index),
        ], fuzzable=fuzzable)


class EditListEntry(Container):
    def __init__(self, segment_duration, media_time, media_rate_integer,
                 media_rate_fraction, fuzzable=True):
        super(EditListEntry, self).__init__(fields=[
            BE32(name="segment_duration", value=segment_duration),
            BE32(name="media_time", value=media_time),
            BE16(name="media_rate_integer", value=media_rate_integer),
            BE16(name="media_rate_fraction", value=media_rate_fraction),
        ], fuzzable=fuzzable)


mp4base = Template(name="mp4base", fields=[
    Mp4Box("ftyp", fields=[
        String(name="majorBrand", value="M4A "),
        BE32(name="majorBrandVersion", value=0x00000200),
        Container(name="compatible brands", fields=[
            String(value="isom"),
            String(value="iso2"),
        ])
    ], fuzzable=False),
    Mp4Box("mdat", fields=[
        Static(name="audiodata", value="""
de0400006c69626661616320312e323800000168ac01c820321004424301
0848221208888261813845bffe0aac951bde667e9e9c7e38d5ea2ab35907
4f54ff627f8de79aedac7cf68ecf968786d07f836ff4b84921ff9ff8c039
3abab7ee3b8dc100418872fe7eef1cb06cf1feffaf9672199fe3e27cfee0
7d600661a4102513ee038260172904005088000e002710066000b8009b80
01049ffd51c7364c8e6f37cf8fdbbff6f3c6b57c000c71fafeaf9fc26002
f8fcfdfdbd9be80ff33fedbfe9be861f7e7fdb7fd37d0c3efcffd5f5bfd8
c3efcf7df5bfd8c045fa7bf4aea9981800281403085000160d6797051bc9
8283d77a00720ff028003e39db7db6b7c1d9fb8f9201fd77efdfab57f6f0
0006fdedfbf7ead50feda8001737efbead4d5000005c6fde6ad46a000014
1bf79081000000170dfbc4018e070110d70a821219844461911845ee6b89
db8bf0d77d77ae78ef5dcadfbeb7e3bf5fbfb6b5abb8b975738193266cd9
f3e8d193266ccebad6839fe1b75dcfa0e7f1cc979887c7c180f7279c0cbe
6317f132fd1465938dddbed5fe6bf26fdc7a1e2e38e38997aaf2a3c4a613
2f980cb9022b6408ad900b79806411018404458058440095800058004c00
02a0002a001c0100170ae6211d886054a28958aa2aaaabbfebfbefdfc7f5
ff6fc71c5f0925e359a1e7f4e7e7e7e7e7f3e7f3e7e779e79e79e79e79e7
9e79e792f25e4bcf25e79fbe79b25af5a5af59afe0580c60c6187e48f9fa
ec2f6000000018f5d956bd61af5835eb986bd606b9cf5cc35c804b580358
0026982404c00013000b819c000580005400380104170ae615088e44300a
9414a5295555e3f3f7df8f9fcff9fae35c5af5412c71f971e3c7e5978f1c
b972c51658a28a28a28a28a28a28a2445122244513c40f50aead4aead4ae
ad4964cb47a3f8c7fbcfef1f99ed9029ffb50d5aa0356a806ad40d55d40d
5a8405750082017215aaa154002a41000001500010000170001302c001c0
01165708ca123888842320884826111a06c2306a76d75eaaf8f5aef8e6f7
7bbe69fa79df7f6f1fe3cf5a9a9c22eeb80f6dbd9d9bf7bafedf6dbd926f
df81f57f43fc6f39f57f43fc7f81f5125fe37c61e68f96836fee5fe377b0
03c8fbc49c08c1e4a28000027df4fc4dbfd03429fb8ff1a00f8c40f8c40f
8805d4fdc07ee2e0348a00e6002e50002e52c00002a05510051400038001
0a9ffd331928488d66f7cf7eff9ff6f3d6aef435cff59ff92121386b6ff8
dfe9fa4e99f48e24fa36b6ff4fd2427d299276c0df93ed42669833b606e2
7da84cd30676c0df43ed42669925e063de7c8dd1525032b167f44f234f9a
f267c87c9e5d57dfa5d1fbfcbc4fc98f4fe15bdd7c81cc6eddc8257d52e6
59e7bd9833bcf3ccd6283506309d508d7ae7af5b61b36361137ef5cd7ada
e61b08837dc35eb9b5cc08800de035eb3580000b80d7300002200bdc0380
00fe9ffd749b2a4d0c66677dff6aff3e757163e9fbb3cf3803e7f03dbece
3d55607cfe07b7c3afaaac0edec3c7c3afefab031c0e5e1d7f2ae604c1db
f76f55cd61305ff1efb4d64c85079fcb057c048afd592c63111668160596
5016600000000007aba371f1d6f5220004481fec767a1f4300dada3e0ece
cf43e87aa001b5b5b4356ad5ac000d9b360d4000003d9b366c0000000d9b
366c000000003fafb2203800c8c0802380""".replace("\n","").decode('hex'))
    ]),
    Mp4Box("moov", fields=[
        Mp4FullBox("mvhd", fields=[
            BE32(name="creationTime", value=0x00000000),
            BE32(name="modificationTime", value=0x00000000),
            BE32(name="timeScale", value=0x000003e8),
            BE32(name="duration", value=0x00000183),
            BE32(name="preferredRate", value=0x00010000),
            BE16(name="preferredVolume", value=0x0100),
            Static(name="reserved1", value="""
000000000000000000000001000000000000000000000000000000010000
000000000000000000000000400000000000000000000000000000000000
00000000000000000000""".replace("\n", "").decode("hex")),
            BE32(name="nextTrackId", value=0x00000002),
        ], fuzzable=False),
        Mp4Box("trak", fuzzable=False, fields=[
            Mp4FullBox("tkhd", flags=0x000003, fields=[
                BE32(name="creation_time", value=0x00000000),
                BE32(name="modification_time", value=0x00000000),
                BE32(name="track id", value=0x00000001),
                BE32(name="reserved1", value=0x00000000),
                BE32(name="duration", value=0x00000183),
                BE32(name="reserved2", value=0x00000000),
                BE32(name="reserved3", value=0x00000000),
                BE16(name="layer", value=0x0000),
                BE16(name="alternate_group", value=0x0001),
                BE16(name="volume", value=0x0100),
                BE16(name="reserved4", value=0x0000),
                Static(name="matrix", value="""
000100000000000000000000000000000001000000000000000000000000
000040000000""".replace("\n", "").decode("hex")),
                BE32(name="width", value=0x00000000),
                BE32(name="height", value=0x00000000),
            ], fuzzable=False),
            Mp4Box("edts", fields=[
                Mp4FullBox("elst", fields=[
                    ElementCount(name="entry_count", depends_on="dataentries", length=32),
                    Container(name="dataentries", fields=[
                        EditListEntry(0x00000154, 0x00000400, 0x0001, 0x0000),
                    ])
                ])
            ]),
            Mp4Box("mdia", fields=[
                Mp4FullBox("mdhd", fields=[
                    BE32(name="creation_time", value=0x00000000),
                    BE32(name="modification_time", value=0x00000000),
                    BE32(name="timescale", value=0x00005622),
                    BE32(name="duration", value=0x00002140),
                    BE16(name="language", value=0x55c4),
                    BE16(name="pre_defined", value=0x0000),
                ], fuzzable=False),
                HdlrBox("soun", "SoundHandler"),
                Mp4Box("minf", fields=[
                    Mp4FullBox("smhd", fields=[
                        BE16(name="balance", value=0),
                        BE16(name="reserved", value=0),
                    ]),
                    Mp4Box("dinf", fields=[
                        Mp4FullBox("dref", fields=[
                            ElementCount(name="entry_count", depends_on="dataentries", length=32),
                            Container(name="dataentries", fields=[
                                Mp4FullBox("url ", flags=0x000001,
                                                            fuzzable=False)

                            ])
                        ])
                    ]),
                    Mp4Box("stbl", fields=[
                        Mp4FullBox("stsd", fields=[
                            ElementCount(name="entry_count", depends_on="dataentries",
                                         length=32),
                            Container(name="dataentries", fuzzable=False, fields=[
                                AudioSampleEntry("mp4a", 1, 2, 16, 0, 0x56220000,
                                                 fields=[
                                                     Mp4FullBox("esds", fields=[
                                                         Static(name="esds_data",
                                                                value="""
0380808022000100048080801440150000000001f4000000628405808080
021388068080800102""".replace("\n", "").decode("hex"))
                                                     ])
                                                 ]),
                            ])
                        ]),
                        Mp4FullBox("stts", fields=[
                            ElementCount(name="entry_count", depends_on="dataentries",
                                         length=32),
                            Container(name="dataentries", fuzzable=False, fields=[
                                TimeToSampleEntry(0x00000008, 0x00000400),
                                TimeToSampleEntry(0x00000001, 0x00000140),
                            ])
                        ]),
                        Mp4FullBox("stsc", fields=[
                            ElementCount(name="entry_count", depends_on="dataentries",
                                         length=32),
                            Container(name="dataentries", fuzzable=False, fields=[
                                SampleToChunkEntry(0x00000001, 0x00000009, 0x00000001),
                            ])
                        ]),
                        Mp4FullBox("stsz", fields=[
                            BE32(name="sample_size", value=0x00000000, fuzzable=False),
                            ElementCount(name="sample_count", depends_on="dataentries",
                                         length=32),
                            Container(name="dataentries", fuzzable=False, fields=[
                                BE32(value=0x00000096),
                                BE32(value=0x000000a4),
                                BE32(value=0x0000008e),
                                BE32(value=0x00000085),
                                BE32(value=0x00000083),
                                BE32(value=0x00000095),
                                BE32(value=0x000000b5),
                                BE32(value=0x000000a1),
                                BE32(value=0x00000006),
                            ])
                        ]),
                        Mp4FullBox("stco", fields=[
                            ElementCount(name="entry_count", depends_on="dataentries",
                                         length=32),
                            Container(name="dataentries", fuzzable=False, fields=[
                                AbsoluteOffset("audiodata", length=32,
                                               encoder=ENC_INT_BE),
                            ])

                        ])
                    ])
                ])
            ]),
        ]),
        Mp4Box("udta", fields=[
            Mp4FullBox("meta", fields=[
                HdlrBox("mdir", ""),
                Mp4Box("ilst", fields=[
                    List(name="metadata_atoms", fields=[
                        Mp4MetadataUtf8Box("\xa9alb", "Album"),
                        Mp4MetadataUtf8Box("\xa9art", "Artist"),
                        Mp4MetadataUtf8Box("aART", "Album Artist"),
                        Mp4MetadataUtf8Box("\xa9cmt", "Comment"),
                        Mp4MetadataUtf8Box("\xa9day", "Year"),
                        Mp4MetadataUtf8Box("\xa9nam", "Title"),
                        Mp4MetadataUtf8Box("\xa9gen", "Genre"),
                        Mp4MetadataBox("trkn", fields=[
                            BE16(name="unknown", value=0x0000),
                            BE16(name="track_number", value=0x0001),
                            BE16(name="total_tracks", value=0x0002),
                            BE16(name="unknown2", value=0x0000),
                        ]),
                        Mp4MetadataBox("disk", fields=[
                            BE16(name="unknown", value=0x0000),
                            BE16(name="disk_number", value=0x0001),
                            BE16(name="total_disks", value=0x0002),
                        ]),
                        Mp4MetadataUtf8Box("\xa9wrt", "Composer"),
                        Mp4MetadataUtf8Box("\xa9too", "Encoder"),
                        Mp4MetadataBox("tmpo", fields=[
                            BE16(name="tempo", value=0x0000),
                        ]),
                        Mp4MetadataUtf8Box("cprt", "Copyright"),
                        Mp4MetadataBox("rtng", fields=[
                            BE8(name="rating", value=0x00),
                        ]),
                        Mp4MetadataUtf8Box("\xa9grp", "Grouping"),
                        Mp4MetadataUtf8Box("catg", "Category"),
                        Mp4MetadataUtf8Box("desc", "Description"),
                        Mp4MetadataUtf8Box("\xa9lyr", "Lyrics"),
                    ])
                ])
            ])
        ])
    ])
])
