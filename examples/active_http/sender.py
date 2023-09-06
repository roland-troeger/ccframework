#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

from ccframework import CCSender, MinimalMicroProtocolSend, ProtocolSendAdapter
from bitstring import Bits
from urllib import request

class ProtocolSendAdapterHTTP(ProtocolSendAdapter):

    def send(self, data: bytes):
        transmission_data = Bits(data)
        if self.microprotocol != None:
            transmission_data = self.microprotocol.preprocess(transmission_data)
        if type(transmission_data) == Bits:
            transmission_data = [transmission_data]
        for some_bits in transmission_data:
            data = some_bits.tobytes()
            req = request.Request("http://localhost:8080", data)
            resp = request.urlopen(req)

mp = MinimalMicroProtocolSend(slice_size=4, padding=Bits(bytes(4)))
adap = ProtocolSendAdapterHTTP(microprotocol=mp)
cc_sender = CCSender([], adap)
cc_sender.send(b'Hello World')
