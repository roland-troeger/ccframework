#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCReceiver, MinimalMicroProtocolReceive, PacketHandlerReceiveFixedPositionPayload, DataPostProcessorBase64
from ccframework.nfq import ProtocolReceiveAdapterNFQ
        
mp = MinimalMicroProtocolReceive(slice_size=64)
ph = PacketHandlerReceiveFixedPositionPayload(start_index=3, slice_size=64)
p_b64 = DataPostProcessorBase64()
adap = ProtocolReceiveAdapterNFQ(queue_id=1, packet_handler=ph,  microprotocol=mp)

ccreceiver = CCReceiver([p_b64], adap)
received_data = ccreceiver.receive()


with open("received.pcap", "wb") as out_file:
    out_file.write(received_data)
