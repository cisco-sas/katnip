from kitty.model import BaseField
from kitty.model.low_level.encoder import ENC_STR_DEFAULT, StrEncoder


class Scapy_Field(BaseField):
    '''
    Represent a scapy_class
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
        super(Scapy_Field, self).__init__(value=str(value), encoder=encoder, fuzzable=fuzzable, name=name)


    def num_mutations(self):
        return self.fuzz_count


    def _mutate(self):
        # during mutation, all we really do is call str(self.fuzz_packet)
        # as scapy performs mutation each time str() is called...
        self._current_value = str(self.fuzz_packet)