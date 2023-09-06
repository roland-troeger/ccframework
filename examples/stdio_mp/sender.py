#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCSender, ProtocolSendAdapterStdio, DataPreProcessorBase64, MinimalMicroProtocolSend

p_b64 = DataPreProcessorBase64()
mp = MinimalMicroProtocolSend(slice_size=4, padding=Bits(bytes(4)))
adap = ProtocolSendAdapterStdio(microprotocol=mp)

cc_sender = CCSender([p_b64], adap)

# "Störsignale" vor und nach der eigentlichen Übertragung zur Demo des (wenn auch primitiven) 
# Mikroprotokolls, das Start und Ende der Übertragung erkennen kann
print("koala")
print("panda")
print("elefant")

cc_sender.send(b'Hello World')

print("löwe")
print("tiger")
print("eisbär")
