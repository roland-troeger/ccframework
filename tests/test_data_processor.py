import random
import unittest

from ccframework import DataPreProcessorBase64, DataPostProcessorBase64, DataPreProcessorAESCTR, DataPostProcessorAESCTR

class TestDataProcessorBase64(unittest.TestCase):

    def test_random_data(self):
        pre = DataPreProcessorBase64()
        post = DataPostProcessorBase64()
        for i in range(1, 64):
            data = random.randbytes(20)
            preprocessed = pre.preprocess(data)
            postprocessed = post.postprocess(preprocessed)
            self.assertNotEqual(data, preprocessed)
            self.assertEqual(data, postprocessed)
    
    def test_known_data(self):
        pre = DataPreProcessorBase64()
        post = DataPostProcessorBase64()

        # decoded data
        plain = [b'', b'123456789', b'oaiwhfiascihowFIOW', b'oiuwefbidiviaosoiwoiii']
        # encoded data
        encoded = [b'', b'MTIzNDU2Nzg5', b'b2Fpd2hmaWFzY2lob3dGSU9X', b'b2l1d2VmYmlkaXZpYW9zb2l3b2lpaQ==']

        for i in range(len(plain)):
            self.assertEqual(encoded[i], pre.preprocess(plain[i]))
        
        for i in range(len(encoded)):
            self.assertEqual(plain[i], post.postprocess(encoded[i]))

class TestDataProcessorAESCTR(unittest.TestCase):

    def test_random_data(self):
        for i in range(1, 16):
            key = random.randbytes(16)
            iv = random.randbytes(8)
            nonce = random.randbytes(8)
            encryptor = DataPreProcessorAESCTR(key, iv, nonce)
            decryptor = DataPostProcessorAESCTR(key, iv, nonce)
            for j in range(1,1024):
                data = random.randbytes(j)
                preprocessed = encryptor.preprocess(data)
                postprocessed = decryptor.postprocess(preprocessed)
                self.assertNotEqual(data, preprocessed)
                self.assertEqual(data, postprocessed)
                
    def test_known_data(self):
        key = b'1234567890abcdef'
        iv = b'12345678'
        nonce = b'90abcdef'
        encryptor = DataPreProcessorAESCTR(key, iv, nonce)
        decryptor = DataPostProcessorAESCTR(key, iv, nonce)

        # Created with Cyberchef AES Encrypt
        # https://cyberchef.org/#recipe=AES_Encrypt(%7B'option':'Latin1','string':'1234567890abcdef'%7D,%7B'option':'Latin1','string':'90abcdef12345678'%7D,'CTR','Raw','Hex',%7B'option':'Hex','string':''%7D)From_Base64('A-Za-z0-9%2B/%3D',true,false/disabled)
        # Settings:
        #  - Key = $key
        #  - IV = $nonce$iv
        #  - Mode = CTR
        #  - Input = Raw
        #  - Output = Hex
        plain = [b'', b'123456789']
        cipher = [b'', bytes.fromhex('372c0e86d89aca39bb')]
        
        for i in range(len(plain)):
            self.assertEqual(cipher[i], encryptor.preprocess(plain[i]))
        for i in range(len(cipher)):
            self.assertEqual(plain[i], decryptor.postprocess(cipher[i]))