#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCReceiver, MinimalMicroProtocolReceive, PacketHandlerReceiveFixedPositionPayload, ProtocolReceiveAdapterPCAP

mp = MinimalMicroProtocolReceive(slice_size=4)
ph = PacketHandlerReceiveFixedPositionPayload(start_index=0, slice_size=4)
adap = ProtocolReceiveAdapterPCAP(
            pcap_file_path="covert_channel_result_filtered.pcap",
            packet_handler=ph,
            microprotocol=mp)

ccreceiver = CCReceiver([], adap)
received = ccreceiver.receive()

print(received.decode("utf-8"))
