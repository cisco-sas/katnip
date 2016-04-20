# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This module was authored and contributed by dark-lbp <jtrkid@gmail.com>
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
from kitty.model import BaseField
from kitty.model.low_level.encoder import ENC_STR_DEFAULT, StrEncoder


class ScapyField(BaseField):
    '''
    Wrap a fuzzed scapy.packet.Packet object as a kitty field.
    Since the fuzzing parameters can be configured by the fuzz function of Scapy,
    this field assumes that the fuzz function was already called on the given field

    :example:

        ::

            from scapy.all import *
            tcp_packet = IP()/TCP()
            field = ScapyField(value=fuzz(tcp_packet), name='tcp packet', fuzz_count=50)

    .. note::

        Due to Scapy's `fuzz()` lack of seed, there's no real reset to this field.
    '''

    _encoder_type_ = StrEncoder

    def __init__(self, value, encoder=ENC_STR_DEFAULT, fuzzable=True, name=None, fuzz_count=1000):
        '''
        :param value: scapy_packet_class
        :type encoder: :class:`~kitty.model.low_levele.encoder.ENC_STR_DEFAULT`
        :param encoder: encoder for the field
        :param fuzzable: is field fuzzable (default: True)
        :param name: name of the object (default: None)
        :param fuzz_count: fuzz count (default: 1000)
        '''
        self.name = name
        self.fuzz_count = fuzz_count
        # keep reference to the field for the _mutate method
        self.fuzz_packet = value
        # pass str(value), as we want the default value to be a string
        super(ScapyField, self).__init__(value=str(value), encoder=encoder, fuzzable=fuzzable, name=name)

    def num_mutations(self):
        '''
        :return: number of mutations this field will perform
        '''
        return self.fuzz_count

    def _mutate(self):
        # during mutation, all we really do is call str(self.fuzz_packet)
        # as scapy performs mutation each time str() is called...
        self._current_value = str(self.fuzz_packet)
