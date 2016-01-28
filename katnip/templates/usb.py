# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
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

'''
USB Protocol tempaltes.
The templates here are based on the USB 2.0 spec.
All page / section references are for the USB 2.0 spec document
The USB 2.0 may be downloaded from:
http://www.usb.org/developers/docs/usb20_docs/usb_20_042814.zip
'''

from kitty.model import *
from katnip.legos.dynamic import DynamicInt


class _StandardRequestCodes:
    '''
    Standard request codes [Section 9.4, table 9.4]
    '''
    GET_STATUS = 0x0
    CLEAR_FEATURE = 0x1
    RESERVED_2 = 0x2
    SET_FEATURE = 0x3
    RESERVED_4 = 0x4
    SET_ADDRESS = 0x5
    GET_DESCRIPTOR = 0x6
    SET_DESCRIPTOR = 0x7
    GET_CONFIGURATION = 0x8
    SET_CONFIGURATION = 0x9
    GET_INTERFACE = 0xa
    SET_INTERFACE = 0xb
    SYNCH_FRAME = 0xc


class _DescriptorTypes:

    '''Descriptor types [Section 9.4, table 9.5]'''

    DEVICE = 0x1
    CONFIGURATION = 0x2
    STRING = 0x3
    INTERFACE = 0x4
    ENDPOINT = 0x5
    DEVICE_QUALIFIER = 0x6
    OTHER_SPEED_CONFIGURATION = 0x7
    INTERFACE_POWER = 0x8
    HUB = 0x29
    CS_INTERFACE = 0x24  # usbcdc11.pdf table 24
    CS_ENDPOINT = 0x25  # usbcdc11.pdf table 24
    DEVICE_HID = 0x21
    REPORT = 0x22


class _StandardFeatureSelector:
    '''Standard feature selectors [Section 9.4, table 9.6]'''
    ENDPOINT_HALT = 0
    DEVICE_REMOTE_WAKEUP = 1
    TEST_MODE = 2


class Descriptor(Template):
    '''
    USB descriptor template.
    '''

    def __init__(self, name, descriptor_type, fields, fuzz_type=True):
        if isinstance(fields, BaseField):
            fields = [fields]
        fields.insert(0, SizeInBytes(name='bLength', sized_field=self, length=8, fuzzable=True))
        fields.insert(1, UInt8(name='bDescriptorType', value=descriptor_type, fuzzable=fuzz_type))
        super(Descriptor, self).__init__(name=name, fields=fields)


class SizedPt(Container):
    '''
    Sized part of a descriptor.
    It receives all fields excepts of the size field and adds it.
    '''
    def __init__(self, name, fields):
        '''
        :param name: name of the Container
        :param fields: list of fields in the container
        '''
        if isinstance(fields, BaseField):
            fields = [fields]
        fields.insert(0, SizeInBytes(name='%s size' % name, sized_field=self, length=8, fuzzable=True))
        super(SizedPt, self).__init__(name=name, fields=fields)


# Device descriptor
# Section 9.6.1, page 261
device_descriptor = Descriptor(
    name='device_descriptor',
    descriptor_type=_DescriptorTypes.DEVICE,
    fields=[
        LE16(name='bcdUSB', value=0x0100),  # USB 2.0 is reported as 0x0200, USB 1.1 as 0x0110 and USB 1.0 as 0x0100
        UInt8(name='bDeviceClass', value=0),
        UInt8(name='bDevuceSubClass', value=0),
        UInt8(name='bDeviceProtocol', value=0),
        UInt8(name='bMaxPacketSize', value=64),  # valid sizes: 8,16,32,64
        LE16(name='idVendor', value=0),
        LE16(name='idProduct', value=0),
        LE16(name='bcdDevice', value=0),
        UInt8(name='iManufacturer', value=0),
        UInt8(name='iProduct', value=0),
        UInt8(name='iSerialNumber', value=0),
        UInt8(name='bNumConfigurations', value=0)
    ])

# Device qualifier descriptor
# Section 9.6.2, page 264
device_qualifier_descriptor = Descriptor(
    name='device_qualifier_descriptor',
    descriptor_type=_DescriptorTypes.DEVICE_QUALIFIER,
    fields=[
        LE16(name='bcdUSB', value=0x0100),  # USB 2.0 is reported as 0x0200, USB 1.1 as 0x0110 and USB 1.0 as 0x0100
        UInt8(name='bDeviceClass', value=0),
        UInt8(name='bDevuceSubClass', value=0),
        UInt8(name='bDeviceProtocol', value=0),
        UInt8(name='bMaxPacketSize', value=0),  # valid sizes: 8,16,32,64
        UInt8(name='bNumConfigurations', value=0),
        UInt8(name='bReserved', value=0)
    ])

'''
'wTotalLength': struct.pack('<H', wTotalLength),
'bNumInterfaces': bytes(bNumInterfaces),
'bConfigurationValue': bytes(self.configuration_index),
'iConfiguration': bytes(self.configuration_string_index),
'bmAttributes': bytes(self.attributes),
'bMaxPower': bytes(self.max_power)
'''
# Configuration descriptor
# Section 9.6.3, page 265
configuration_descriptor = Descriptor(
    name='configuration_descriptor',
    descriptor_type=_DescriptorTypes.CONFIGURATION,
    fields=[
        DynamicInt('wTotalLength', LE16(value=9)),
        DynamicInt('bNumInterfaces', UInt8(value=1)),
        DynamicInt('bConfigurationValue', UInt8(value=1)),
        DynamicInt('iConfiguration', UInt8(value=0)),
        DynamicInt('bmAttributes', BitField(value=0, length=8)),
        DynamicInt('bMaxPower', UInt8(value=1)),
    ])


# Other_Speed_Configuration descriptor
# Section 9.6.4, page 267
other_speed_configuration_descriptor = Descriptor(
    name='other_speed_configuration_descriptor',
    descriptor_type=_DescriptorTypes.OTHER_SPEED_CONFIGURATION,
    fields=[
        LE16(name='wTotalLength', value=0xffff),  # TODO: real default size
        UInt8(name='bNumInterfaces', value=0xff),  # TODO: real default size
        UInt8(name='bConfigurationValue', value=0xff),  # TODO: real default size
        UInt8(name='iConfiguration', value=0xff),
        BitField(name='bmAttributes', value=0, length=8),
        UInt8(name='bMaxPower', value=0xff)
    ])


# Interface descriptor
# Section 9.6.5, page 267
interface_descriptor = Descriptor(
    name='interface_descriptor',
    descriptor_type=_DescriptorTypes.INTERFACE,
    fields=[
        DynamicInt('bInterfaceNumber', UInt8(value=0)),
        DynamicInt('bAlternateSetting', UInt8(value=0)),
        DynamicInt('bNumEndpoints', UInt8(value=0x1)),
        DynamicInt('bInterfaceClass', UInt8(value=0x08)),  # 0x08 mass storage
        DynamicInt('bInterfaceSubClass', UInt8(value=0x06)),  # 0x06 mass storage
        DynamicInt('bInterfaceProtocol', UInt8(value=0x50)),  # 0x50 mass storage
        DynamicInt('iInterface', UInt8(value=0)),
    ])


# Endpoint descriptor
# Section 9.6.6, page 269
endpoint_descriptor = Descriptor(
    name='endpoint_descriptor',
    descriptor_type=_DescriptorTypes.ENDPOINT,
    fields=[
        UInt8(name='bEndpointAddress', value=0),
        BitField(name='bmAttributes', value=0, length=8),
        LE16(name='wMaxPacketSize', value=65535),
        UInt8(name='bInterval', value=0)
    ])


# String descriptor (regular and zero)
# Section 9.6.7, page 273
string_descriptor = Descriptor(
    name='string_descriptor',
    descriptor_type=_DescriptorTypes.STRING,
    fields=[
        String(name='bString', value='hello_kitty', encoder=StrEncodeEncoder('utf_16_le'), max_size=254/2)
    ])


string_descriptor_zero = Descriptor(
    name='string_descriptor_zero',
    descriptor_type=_DescriptorTypes.STRING,
    fields=[
        RandomBytes(name='lang_id', min_length=0, max_length=253, step=3, value='\x04\x09')
    ])

hub_descriptor = Descriptor(
    name='hub_descriptor',
    descriptor_type=_DescriptorTypes.HUB,
    fields=[
        UInt8(name='bNbrPorts', value=4),
        BitField(name='wHubCharacteristics', value=0xe000, length=16),
        UInt8(name='bPwrOn2PwrGood', value=0x32),
        UInt8(name='bHubContrCurrent', value=0x64),
        UInt8(name='DeviceRemovable', value=0),
        UInt8(name='PortPwrCtrlMask', value=0xff)
    ])


###################################################
#              Mass Storage Templates             #
###################################################

# USBMassStorageClass
reset_request = Template(
    name='reset_request',
    fields=String(name='reset response', value=''))


# USBMassStorageClass
max_lun = Template(
    name='max_lun',
    fields=UInt8(name='Max_LUN', value=0x00))


# Request Sence - FuzzableUSBMassStorageInterface
SCSI_op_code_0x03 = Template(
    name='SCSI_op_code_0x03',
    fields=[
        UInt8(name='ResponseCode', value=0x70),
        UInt8(name='VALID', value=0x00),
        UInt8(name='Obsolete', value=0x00),
        UInt8(name='SenseKey', value=0x00),
        UInt8(name='Resv', value=0x00),
        UInt8(name='ILI', value=0x00),
        UInt8(name='EOM', value=0x00),
        UInt8(name='FILEMARK', value=0x00),
        BE32(name='Information', value=0x00),
        SizedPt(name='Additional_Sense_data',
                fields=[
                    BE32(name='CmdSpecificInfo', value=0x00),
                    UInt8(name='ASC', value=0x00),
                    UInt8(name='ASCQ', value=0x00),
                    UInt8(name='FRUC', value=0x00),
                    UInt8(name='SenseKeySpecific_0', value=0x00),
                    UInt8(name='SenseKeySpecific_1', value=0x00),
                    UInt8(name='SenseKeySpecific_2', value=0x00),
                ])
    ])


# Inquiry - FuzzableUSBMassStorageInterface
SCSI_op_code_0x12 = Template(
    name='SCSI_op_code_0x12',
    fields=[
        UInt8(name='Peripheral', value=0x00),
        UInt8(name='Removable', value=0x80),
        UInt8(name='Version', value=0x04),
        UInt8(name='Response_Data_Format', value=0x02),
        SizedPt(name='Additional Inquiry Data',
                fields=[
                    UInt8(name='Sccstp', value=0x00),
                    UInt8(name='Bqueetc', value=0x00),
                    UInt8(name='CmdQue', value=0x00),
                    Pad(8 * 8, fields=String(name='VendorID', value='HeloKitt', max_size=8)),
                    Pad(16 * 8, fields=String(name='ProductID', value='SAS - HelloKitty', max_size=16)),
                    Pad(4 * 8, fields=String(name='productRev', value='1234', max_size=4)),
                ])
    ])


# Mode Sence - FuzzableUSBMassStorageInterface
SCSI_op_code_0x1a_or_0x5a = Template(
    name='SCSI_op_code_0x1a_or_0x5a',
    fields=[
        SizeInBytes(name='bLength', sized_field='SCSI_op_code_0x1a_or_0x5a', length=8, fuzzable=True),
        UInt8(name='MediumType', value=0x00),
        UInt8(name='Device_Specific_Param', value=0x00),
        SizedPt(name='Mode_Parameter_Container', fields=RandomBytes(name='Mode_Parameter', min_length=0, max_length=4, value='\x1c'))
    ])


# Read Format Capacity - FuzzableUSBMassStorageInterface
SCSI_op_code_0x23 = Template(
    name='SCSI_op_code_0x23',
    fields=[
        BE32(name='capacity_list_length', value=0x8),
        BE32(name='num_of_blocks', value=0x1000),
        BE16(name='descriptor_code', value=0x1000),
        BE16(name='block_length', value=0x0200)
    ])


# Read Capacity - FuzzableUSBMassStorageInterface
SCSI_op_code_0x25 = Template(
    name='SCSI_op_code_0x25',
    fields=[
        BE32(name='NumBlocks', value=0x4fff),
        BE32(name='BlockLen', value=0x200)
    ])


# Read 10- FuzzableUSBMassStorageInterface
SCSI_op_code_0x28 = Template(
    name='SCSI_op_code_0x28',
    fields=[
        RandomBytes(name='Random_Block_Data', min_length=0, max_length=512 * 160, step=(512 / 4 * 3), value='\x00')
    ])


###################################################
#              CDC Class Templates                #
###################################################
class _CDC_DescriptorSubTypes:  # CDC Functional Descriptors

    '''Descriptor sub types [usbcdc11.pdf table 25]'''

    HEADER_FUNCTIONAL = 0
    CALL_MANAGMENT = 1
    ABSTRACT_CONTROL_MANAGEMENT = 2
    DIRECT_LINE_MANAGEMENT = 3
    TELEPHONE_RINGER = 4
    TELEPHONE_CALL = 5
    UNION_FUNCTIONAL = 6
    COUNTRY_SELECTION = 7
    TELEPHONE_OPERATIONAL_MODES = 8
    USB_TERMINAL = 9
    NETWORK_CHANNEL_TERMINAL = 0xa
    PROTOCOL_UNIT = 0xb
    EXTENSION_UNIT = 0xc
    MULTI_CHANNEL_MANAGEMENT = 0xd
    CAPI_CONTROL_MANAGEMENT = 0xe
    ETHERNET_NETWORKING = 0xf
    ATM_NETWORKING = 0x10
    # 0x11-0xff reserved


cdc_header_functional_descriptor = Descriptor(
    name='cdc_header_functional_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_CDC_DescriptorSubTypes.HEADER_FUNCTIONAL),
        LE16(name='bcdCDC', value=0xffff)
    ])


cdc_call_management_functional_descriptor = Descriptor(
    name='cdc_call_management_functional_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_CDC_DescriptorSubTypes.CALL_MANAGMENT),
        BitField(name='bmCapabilities', value=0, length=8),
        UInt8(name='bDataInterface', value=0)
    ])


# TODO: Missing descriptors for subtypes 3,4,5

cdc_abstract_control_management_functional_descriptor = Descriptor(
    name='cdc_abstract_control_management_functional_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_CDC_DescriptorSubTypes.ABSTRACT_CONTROL_MANAGEMENT),
        BitField(name='bmCapabilities', value=0, length=8)
    ])


cdc_union_functional_descriptor = Descriptor(
    name='cdc_union_functional_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_CDC_DescriptorSubTypes.UNION_FUNCTIONAL),
        UInt8(name='bMasterInterface', value=0),
        Repeat(UInt8(name='bSlaveInterfaceX', value=0), 0, 251)
    ])


# TODO: Missing descriptors 7,8,9,10,11,12,13,14

cdc_ethernet_networking_functional_descriptor = Descriptor(
    name='cdc_ethernet_networking_functional_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_CDC_DescriptorSubTypes.ETHERNET_NETWORKING),
        UInt8(name='iMACAddress', value=0),
        BitField(name='bmEthernetStatistics', value=0xffffffff, length=32),
        LE16(name='wMaxSegmentSize', value=1514),
        LE16(name='wNumberMCFilters', value=0),
        UInt8(name='bNumberPowerFilters', value=0)
    ])


###################################################
#              Audio Class Templates              #
###################################################
class _AC_DescriptorSubTypes:  # AC Interface Descriptor Subtype

    '''Descriptor sub types [audio10.pdf table A-5]'''

    AC_DESCRIPTOR_UNDEFINED = 0x00
    HEADER = 0x01
    INPUT_TERMINAL = 0x02
    OUTPUT_TERMINAL = 0x03
    MIXER_UNIT = 0x04
    SELECTOR_UNIT = 0x05
    FEATURE_UNIT = 0x06
    PROCESSING_UNIT = 0x07
    EXTENSION_UNIT = 0x08


class _AS_DescriptorSubTypes:  # AS Interface Descriptor Subtype

    '''Descriptor sub types [audio10.pdf table A-6]'''

    AS_DESCRIPTOR_UNDEFINED = 0x00
    AS_GENERAL = 0x01
    FORMAT_TYPE = 0x02
    FORMAT_SPECIFIC = 0x03


adc_header_descriptor = Descriptor(
    name='adc_header_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_AC_DescriptorSubTypes.HEADER),
        LE16(name='bcdADC', value=0x0100),
        LE16(name='wTotalLength', value=0x1e),
        UInt8(name='bInCollection', value=0x1),
        Repeat(UInt8(name='baInterfaceNrX', value=1), 0, 247)
    ])


adc_input_terminal_descriptor = Descriptor(
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    name='adc_input_terminal_descriptor',
    fields=[
        UInt8(name='bDesciptorSubType', value=_AC_DescriptorSubTypes.INPUT_TERMINAL),
        UInt8(name='bTerminalID', value=0x00),
        LE16(name='wTerminalType', value=0x0206),  # termt10.pdf table 2-2
        UInt8(name='bAssocTerminal', value=0x00),
        UInt8(name='bNrChannels', value=0x01),
        LE16(name='wChannelConfig', value=0x0101),
        UInt8(name='iChannelNames', value=0x00),
        UInt8(name='iTerminal', value=0x00)
    ])


adc_output_terminal_descriptor = Descriptor(
    name='adc_output_terminal_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_AC_DescriptorSubTypes.OUTPUT_TERMINAL),
        UInt8(name='bTerminalID', value=0x00),
        LE16(name='wTerminalType', value=0x0307),  # termt10.pdf table 2-3
        UInt8(name='bAssocTerminal', value=0x00),
        UInt8(name='bSourceID', value=0x01),
        UInt8(name='iTerminal', value=0x00)
    ])

# TODO skipping a few descriptors...

# Table 4-7
adc_feature_unit_descriptor = Descriptor(
    name='adc_feature_unit_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_AC_DescriptorSubTypes.FEATURE_UNIT),
        UInt8(name='bUnitID', value=0x00),
        UInt8(name='bSourceID', value=0x00),
        SizedPt(name='bmaControls',
                fields=RandomBytes(name='bmaControlsX', value='\x00', min_length=0, step=17, max_length=249)),
        UInt8(name='iFeature', value=0x00)
    ])


# Table 4-19
adc_as_interface_descriptor = Descriptor(
    name='adc_as_interface_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_AS_DescriptorSubTypes.AS_GENERAL),
        UInt8(name='bTerminalLink', value=0x00),
        UInt8(name='bDelay', value=0x00),
        LE16(name='wFormatTag', value=0x0001)
    ])


adc_as_format_type_descriptor = Descriptor(
    name='adc_as_format_type_descriptor',
    descriptor_type=_DescriptorTypes.CS_INTERFACE,
    fields=[
        UInt8(name='bDesciptorSubType', value=_AS_DescriptorSubTypes.FORMAT_TYPE),
        UInt8(name='bFormatType', value=0x01),
        UInt8(name='bNrChannels', value=0x01),
        UInt8(name='bSubFrameSize', value=0x02),
        UInt8(name='bBitResolution', value=0x10),
        UInt8(name='bSamFreqType', value=0x01),
        BitField(name='tSamFreq', length=24, value=0x01F40)
    ])


###################################################
#              HID Class Templates                #
###################################################

hid_configuration_descriptor = Descriptor(
    name='hid_configuration_descriptor',
    descriptor_type=_DescriptorTypes.CONFIGURATION,
    fields=[
        LE16(name='wTotalLength', value=9),  # TODO: use sizer ?
        UInt8(name='bNumInterfaces', value=1),
        UInt8(name='bConfigurationValue', value=1),
        UInt8(name='iConfiguration', value=0),
        BitField(name='bmAttributes', value=0xa0, length=8),
        UInt8(name='bMaxPower', value=0x32)
    ])

hid_interface_descriptor = Descriptor(
    name='hid_interface_descriptor',
    descriptor_type=_DescriptorTypes.INTERFACE,
    fields=[
        UInt8(name='bInterfaceNumber', value=0),
        UInt8(name='bAlternateSetting', value=0),
        UInt8(name='bNumEndpoints', value=0x2),
        UInt8(name='bInterfaceClass', value=0x03),  # 0x08 HID
        UInt8(name='bInterfaceSubClass', value=0x00),
        UInt8(name='bInterfaceProtocol', value=0x00),
        UInt8(name='iInterface', value=0)
    ])

hid_hid_descriptor = Descriptor(
    name='hid_hid_descriptor',
    descriptor_type=_DescriptorTypes.DEVICE_HID,
    fields=[
        LE16(name='bcdHID', value=0x0110),
        UInt8(name='bCountryCode', value=0x00),
        UInt8(name='bNumDescriptors', value=0x01),
        UInt8(name='bReportDescriptorType', value=_DescriptorTypes.REPORT, fuzzable=True),
        LE16(name='wDescriptorLength', value=0x002f),  # should be changed ??
    ])

# Crashing windows
# s_initialize('interface_descriptor')
# s_sizer(name='bLength', block_name='descriptor_block', length=1, fuzzable=False, inclusive=True)  # 9 Bytes
# if s_block_start('descriptor_block'):
#     UInt8(name='bDescriptorType', value=_DescriptorTypes.INTERFACE, fuzzable=True),
#     s_byte(name='bInterfaceNumber', value=0, fuzzable=False)
#     s_byte(name='bAlternateSetting', value=0, fuzzable=False)
#     s_byte(name='bNumEndpoints', value=0, fuzzable=False)
#     s_byte(name='bInterfaceClass', value=0x08, fuzzable=False)
#     s_byte(name='bInterfaceSubClass', value=0x06, fuzzable=False)
#     s_byte(name='bInterfaceProtocol', value=0x50, fuzzable=False)
#     s_byte(name='iInterface', value=0, fuzzable=True)
# s_block_end('descriptor_block')
