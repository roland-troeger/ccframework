#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCSender, MinimalMicroProtocolSend, PacketHandlerSendFixedPositionPayload, DataPreProcessorBase64
from ccframework.nfq import ProtocolSendAdapterNFQ

mp = MinimalMicroProtocolSend(slice_size=64, padding=Bits(bytes(64)))
ph = PacketHandlerSendFixedPositionPayload(start_index=3, slice_size=64)
p_b64 = DataPreProcessorBase64()
adap = ProtocolSendAdapterNFQ(queue_id=0, packet_handler=ph, microprotocol=mp)

cc_sender = CCSender([p_b64], adap)

with open("../pcap/covert_channel_result_filtered.pcap", "rb") as in_file:
    file_data = in_file.read()
    cc_sender.send(file_data)
