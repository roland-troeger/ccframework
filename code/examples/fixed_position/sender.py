#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCSender, MinimalMicroProtocolSend, PacketHandlerSendFixedPositionPayload
from ccframework.nfq import ProtocolSendAdapterNFQ

mp = MinimalMicroProtocolSend(slice_size=7, padding=Bits(bytes(4)), unit='bits')
ph = PacketHandlerSendFixedPositionPayload(start_index=3, slice_size=7, unit='bits')
adap = ProtocolSendAdapterNFQ(queue_id=0, packet_handler=ph, microprotocol=mp)

cc_sender = CCSender([], adap)
cc_sender.send(b'Hello World')
