#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCReceiver, MinimalMicroProtocolReceive, PacketHandlerReceiveFixedPositionPayload
from ccframework.nfq import ProtocolReceiveAdapterNFQ
        
mp = MinimalMicroProtocolReceive(slice_size=7, unit='bits')
ph = PacketHandlerReceiveFixedPositionPayload(start_index=3, slice_size=7, unit='bits')
adap = ProtocolReceiveAdapterNFQ(queue_id=1, packet_handler=ph,  microprotocol=mp)

ccreceiver = CCReceiver([], adap)
received = ccreceiver.receive()

print(received.decode("utf-8"))
