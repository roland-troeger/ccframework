#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from ccframework import CCReceiver, MinimalMicroProtocolReceive, PacketHandlerReceive
from ccframework.nfq import ProtocolReceiveAdapterNFQ

from bitstring import Bits
from scapy.all import *

class PacketHandlerReceiveNFQReplaceUDPayload(PacketHandlerReceive):
    def handle_packet(self, packet):
        if UDP in packet and Raw in packet:
            payload_raw = packet[UDP].payload
            bits_in = Bits(bytes(payload_raw))
            return bits_in

mp = MinimalMicroProtocolReceive(slice_size=4)
ph = PacketHandlerReceiveNFQReplaceUDPayload()
adap = ProtocolReceiveAdapterNFQ(queue_id=1, microprotocol=mp, packet_handler=ph)

ccreceiver = CCReceiver([], adap)
received = ccreceiver.receive()

print(received.decode("utf-8"))
