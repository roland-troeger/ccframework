#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCReceiver, MinimalMicroProtocolReceive, PacketHandlerReceiveRegexPayload, DataPostProcessorBase64
from ccframework.nfq import ProtocolReceiveAdapterNFQ
        
post_b64 = DataPostProcessorBase64()
mp = MinimalMicroProtocolReceive(slice_size=4)
ph = PacketHandlerReceiveRegexPayload(regex=r'1234(.*)abcdefg')
adap = ProtocolReceiveAdapterNFQ(queue_id=1, packet_handler=ph,  microprotocol=mp)

ccreceiver = CCReceiver([post_b64], adap)
received = ccreceiver.receive()

print(received.decode("utf-8"))
