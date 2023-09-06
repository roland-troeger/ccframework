#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from ccframework import DataPreProcessorAESCTR, CCSender, ProtocolSendAdapterStdio, DataPreProcessorBase64

aes_key = b'16randombytesabc'
aes_iv = b'12345678'
aes_nonce = b'90abcdef'

p_aes = DataPreProcessorAESCTR(aes_key, aes_iv, aes_nonce)
p_b64 = DataPreProcessorBase64()
adap = ProtocolSendAdapterStdio()

cc_sender = CCSender([p_aes, p_b64], adap)
cc_sender.send(b'Hello World')
