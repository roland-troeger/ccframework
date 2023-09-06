#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from ccframework import DataPostProcessorAESCTR, CCReceiver, DataPostProcessorBase64, ProtocolReceiveAdapterStdio

aes_key = b'16randombytesabc'
aes_iv = b'12345678'
aes_nonce = b'90abcdef'

p_aes = DataPostProcessorAESCTR(aes_key, aes_iv, aes_nonce)
p_b64 = DataPostProcessorBase64()
adap = ProtocolReceiveAdapterStdio()

ccreceiver = CCReceiver([p_b64, p_aes], adap)
received = ccreceiver.receive()

print(received.decode("utf-8"))
