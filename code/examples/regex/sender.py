#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits
from ccframework import CCSender, DataPreProcessorBase64, MinimalMicroProtocolSend, PacketHandlerSendRegexPayload
from ccframework.nfq import ProtocolSendAdapterNFQ

pre_b64 = DataPreProcessorBase64()
mp = MinimalMicroProtocolSend(slice_size=4, padding=Bits(bytes(4)))
ph = PacketHandlerSendRegexPayload(regex=r'[567890]+')
adap = ProtocolSendAdapterNFQ(queue_id=0, packet_handler=ph, microprotocol=mp)

cc_sender = CCSender([pre_b64], adap)
cc_sender.send(b'Hello World')
