import random
from bitstring import Bits
import unittest

from ccframework import SimpleBitSlicer

class TestBitSlicer(unittest.TestCase):

    def test_long_bitstring(self):
        slicer = SimpleBitSlicer(slice_size=3, padding=Bits('0b0000'))
        test_data = '0101001010110101'
        desired_result = ['010','100', '101', '011', '010', '100']
        actual_result = slicer.slice(Bits(f"0b{test_data}"))
        self.assertEqual(len(desired_result), len(actual_result))
        for i in range(len(desired_result)):
            self.assertEqual(actual_result[i], Bits(f"0b{desired_result[i]}"))
    

    def test_single_bit(self):
        slicer = SimpleBitSlicer(slice_size=3, padding=Bits('0b0000'))
        test_data = '1'
        desired_result = ['100']
        actual_result = slicer.slice(Bits(f"0b{test_data}"))
        self.assertEqual(len(desired_result), len(actual_result))
        for i in range(len(desired_result)):
            self.assertEqual(actual_result[i], Bits(f"0b{desired_result[i]}"))
