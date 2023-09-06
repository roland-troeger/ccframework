#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCReceiver, DataPostProcessorBase64, ProtocolReceiveAdapterStdio, MinimalMicroProtocolReceive

p_b64 = DataPostProcessorBase64()
mp = MinimalMicroProtocolReceive(slice_size=4)
adap = ProtocolReceiveAdapterStdio(microprotocol=mp)

ccreceiver = CCReceiver([p_b64], adap)
received = ccreceiver.receive()

print(received.decode("utf-8"))
