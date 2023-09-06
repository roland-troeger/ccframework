import random
from bitstring import Bits
import unittest

from ccframework import MinimalMicroProtocolSend, MinimalMicroProtocolReceive, TransmissionState

class TestMinimalMicroProtocolSend(unittest.TestCase):
    
    def test_unit_bits(self):
        for i in range(0,20):
            slice_size = random.randint(1, 99)
            mp = MinimalMicroProtocolSend(slice_size=slice_size, unit=MinimalMicroProtocolSend.BITS, padding=Bits('0b'+('0'*(slice_size))))
            self.assertEqual(slice_size, mp.slice_size)

    def test_unit_bytes(self):
        for i in range(0,20):
            slice_size = random.randint(1, 99)
            mp = MinimalMicroProtocolSend(slice_size=slice_size, unit=MinimalMicroProtocolSend.BYTES, padding=Bits(bytes(slice_size)))
            self.assertEqual(slice_size*8, mp.slice_size)
        for i in range(0,20):
            slice_size = random.randint(1, 99)
            mp = MinimalMicroProtocolSend(slice_size=slice_size, padding=Bits(bytes(slice_size)))
            self.assertEqual(slice_size*8, mp.slice_size)
    
    def test_preprocess(self):
        test_data = '0111101001010110101'
        desired_result = ['000', '011', '110', '100', '101', '011', '010', '100','000']

        mp = MinimalMicroProtocolSend(slice_size=3, unit=MinimalMicroProtocolSend.BITS, padding=Bits('0b00'))
        actual_result = mp.preprocess(Bits(f"0b{test_data}"))

        self.assertEqual(len(desired_result), len(actual_result))
        for i in range(len(desired_result)):
            self.assertEqual(actual_result[i], Bits(f"0b{desired_result[i]}"))
    
class TestMinimalMicroProtocolReceive(unittest.TestCase):
    def test_unit_bits(self):
        for i in range(0,20):
            slice_size = random.randint(1, 99)
            mp = MinimalMicroProtocolReceive(slice_size=slice_size, unit=MinimalMicroProtocolReceive.BITS)
            self.assertEqual(slice_size, mp.slice_size)

    def test_unit_bytes(self):
        for i in range(0,20):
            slice_size = random.randint(1, 99)
            mp = MinimalMicroProtocolReceive(slice_size=slice_size, unit=MinimalMicroProtocolReceive.BYTES)
            self.assertEqual(slice_size*8, mp.slice_size)
        for i in range(0,20):
            slice_size = random.randint(1, 99)
            mp = MinimalMicroProtocolReceive(slice_size=slice_size)
            self.assertEqual(slice_size*8, mp.slice_size)

    def test_postprocess(self):
        mp = MinimalMicroProtocolReceive(slice_size=3, unit=MinimalMicroProtocolReceive.BITS)
        self.assertEqual(mp.transmission_state, TransmissionState.WAITING_FOR_TRANSMISSION)

        resp = mp.postprocess(Bits('0b001'))
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.transmission_state, TransmissionState.WAITING_FOR_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.WAITING_FOR_TRANSMISSION)

        resp = mp.postprocess(Bits('0b000'))
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.transmission_state, TransmissionState.ACTIVE_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.ACTIVE_TRANSMISSION)

        resp = mp.postprocess(Bits('0b110'))
        self.assertEqual(resp.data, Bits('0b110'))
        self.assertEqual(resp.transmission_state, TransmissionState.ACTIVE_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.ACTIVE_TRANSMISSION)

        resp = mp.postprocess(Bits('0b011'))
        self.assertEqual(resp.data, Bits('0b011'))
        self.assertEqual(resp.transmission_state, TransmissionState.ACTIVE_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.ACTIVE_TRANSMISSION)

        resp = mp.postprocess(Bits('0b000'))
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.transmission_state, TransmissionState.FINISHED_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.FINISHED_TRANSMISSION)

        resp = mp.postprocess(Bits('0b111'))
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.transmission_state, TransmissionState.FINISHED_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.FINISHED_TRANSMISSION)

        resp = mp.postprocess(Bits('0b000'))
        self.assertEqual(resp.data, None)
        self.assertEqual(resp.transmission_state, TransmissionState.FINISHED_TRANSMISSION)
        self.assertEqual(mp.transmission_state, TransmissionState.FINISHED_TRANSMISSION)
