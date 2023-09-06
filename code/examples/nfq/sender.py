#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from ccframework import CCSender, MinimalMicroProtocolSend, PacketHandlerSend
from ccframework.nfq import ProtocolSendAdapterNFQ

from bitstring import Bits
from scapy.all import *

class PacketHandlerSendReplaceUDPayload(PacketHandlerSend):
    def handle_packet(self, packet):
        if UDP in packet and Raw in packet:
            bits_to_send = self.send_buffer.pop(0)
            packet[UDP].payload = Raw(bits_to_send.tobytes())

mp = MinimalMicroProtocolSend(slice_size=4, padding=Bits(bytes(4)))
ph = PacketHandlerSendReplaceUDPayload()
adap = ProtocolSendAdapterNFQ(queue_id=0, microprotocol=mp, packet_handler=ph)

cc_sender = CCSender([], adap)
cc_sender.send(b'Hello World')
