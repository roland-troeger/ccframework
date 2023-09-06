#import random
from bitstring import Bits
import unittest
from scapy.all import *

from ccframework import PacketHandlerSendFixedPositionPayload, PacketHandlerReceiveFixedPositionPayload
from ccframework import PacketHandlerSendRegexPayload, PacketHandlerReceiveRegexPayload
from ccframework import ProtocolReceiveAdapter

class TestPacketHandlerSendFixedPositionPayload(unittest.TestCase):

    def test_known_data_bytes(self):
        test_payloads = [b'123456789012', b'abcdefghijkl', b'qwertzuiopasdfghjkl']
        test_injection_data = [Bits(b'abcdefg'), Bits(b'fkmcjyi'), Bits(b'12j7xge')]
        test_result = [b'123abcdefg12', b'abcfkmcjyikl', b'qwe12j7xgeasdfghjkl']

        ph = PacketHandlerSendFixedPositionPayload(start_index=3, slice_size=7, unit='bytes')
        ph.set_send_buffer(test_injection_data)

        for i in range(len(test_payloads)):
            packet = UDP()/Raw(test_payloads[i])
            ph.handle_packet(packet)
            self.assertEqual(bytes(packet[UDP].payload), test_result[i])
    
    def test_replace_full_payload(self):
        test_payload = b'abcdefgh'
        test_injection_data = [Bits(b'12345678')]
        test_result = b'12345678'

        ph = PacketHandlerSendFixedPositionPayload(start_index=0, slice_size=8, unit='bytes')
        ph.set_send_buffer(test_injection_data)
        packet = UDP()/Raw(test_payload)
        ph.handle_packet(packet)
        self.assertEqual(bytes(packet[UDP].payload), test_result)

    def test_known_data_bits(self):
        test_payloads = [Bits(bin='1001010100100110'), Bits(bin='1001010100100110'), Bits(bin='1001010100100110')]
        test_injection_data = [Bits(bin='0110100'), Bits(bin='1110010'), Bits(bin='0100101')]
        test_result = [Bits(bin='1000110100100110'),Bits(bin='1001110010100110'),Bits(bin='1000100101100110')]

        ph = PacketHandlerSendFixedPositionPayload(start_index=3, slice_size=7, unit='bits')
        ph.set_send_buffer(test_injection_data)

        for i in range(len(test_payloads)):
            packet = UDP()/Raw(test_payloads[i].tobytes())
            ph.handle_packet(packet)
            self.assertEqual(Bits(bytes(packet[UDP].payload)), test_result[i])

class TestPacketHandlerReceiveFixedPositionPayload(unittest.TestCase):
    
    def test_known_data_bytes(self):
        test_payloads = [b'123abcdefg12', b'abcfkmcjyikl', b'qwe12j7xgeasdfghjkl']
        desired_result = [b'abcdefg', b'fkmcjyi', b'12j7xge']

        ph = PacketHandlerReceiveFixedPositionPayload(start_index=3, slice_size=7, unit='bytes')

        for i in range(len(test_payloads)):
            packet = UDP()/Raw(test_payloads[i])
            result = ph.handle_packet(packet)
            self.assertEqual(result, desired_result[i])

    def test_replace_full_payload(self):
        test_payload = b'12345678'
        desired_result = b'12345678'

        ph = PacketHandlerReceiveFixedPositionPayload(start_index=0, slice_size=8, unit='bytes')

        packet = UDP()/Raw(test_payload)
        res = ph.handle_packet(packet)
        self.assertEqual(res, desired_result)

    def test_known_data_bits(self):
        test_payloads = [Bits(bin='1000110100100110'),Bits(bin='1001110010100110'),Bits(bin='1000100101100110')]
        desired_result = [Bits(bin='0110100'), Bits(bin='1110010'), Bits(bin='0100101')]

        ph = PacketHandlerReceiveFixedPositionPayload(start_index=3, slice_size=7, unit='bits')

        for i in range(len(test_payloads)):
            packet = UDP()/Raw(test_payloads[i].tobytes())
            result = ph.handle_packet(packet)
            self.assertEqual(result, desired_result[i])


class TestPacketHandlerSendRegexPayload(unittest.TestCase):
    def test_known_data(self):
        test_payload = b'1234567890abcdefg'
        test_injection_data = [Bits(b'Hell'), Bits(b'o Wo'), Bits(b'rld\n')]
        test_result = [b'1234Hellabcdefg', b'1234o Woabcdefg', b'1234rld\nabcdefg']

        ph = PacketHandlerSendRegexPayload(regex=r'[567890]+')
        ph.set_send_buffer(test_injection_data)

        for i in range(len(test_result)):
            packet = UDP()/Raw(test_payload)
            ph.handle_packet(packet)
            self.assertEqual(bytes(packet[UDP].payload), test_result[i])

class TestPacketHandlerReceiveRegexPayload(unittest.TestCase):
    def test_known_data(self):
        test_payloads = [b'1234Hellabcdefg', b'1234o Woabcdefg', b'1234rld1abcdefg']
        desired_result = [Bits(b'Hell'), Bits(b'o Wo'), Bits(b'rld1')]

        ph = PacketHandlerReceiveRegexPayload(regex=r'1234(.*)abcdefg')

        for i in range(len(test_payloads)):
            packet = UDP()/Raw(test_payloads[i])
            print(f"pl={test_payloads[i]}")
            result = ph.handle_packet(packet)
            self.assertEqual(result, desired_result[i])
