#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from bitstring import Bits

from ccframework import CCSender, MinimalMicroProtocolSend, PacketHandlerSendFixedPositionPayload, ProtocolSendAdapterPCAP

mp = MinimalMicroProtocolSend(slice_size=4, padding=Bits(bytes(4)))
ph = PacketHandlerSendFixedPositionPayload(start_index=0, slice_size=4)
adap = ProtocolSendAdapterPCAP(
            pcap_file_path="dns_requests.pcap",
            new_src_ip="127.0.0.1",
            new_dst_ip="127.0.0.1",
            new_src_mac="00:00:00:00:00:00",
            new_dst_mac="00:00:00:00:00:00",
            new_dst_port=56565,
            packet_handler=ph, 
            microprotocol=mp)

cc_sender = CCSender([], adap)
cc_sender.send(b'Hello World')
