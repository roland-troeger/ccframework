from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import cached_property

from bitstring import Bits

from ccframework import ProtocolReceiveAdapter, MinimalMicroProtocolReceive, CCReceiver, TransmissionState

#!/usr/bin/env python3
if __name__ != '__main__':
    exit()

class CovertHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        #content_len = int(self.headers.get('Content-Length'))
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length)
        print(f"received post body: {post_body}")
        RECEIVE_ADAPTER.handle_received_data(Bits(post_body))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes())

class ProtocolReceiveAdapterHTTP(ProtocolReceiveAdapter):
    def receive(self) -> bytes:
        webServer = HTTPServer(("localhost", 8080), CovertHTTPHandler)
        try:
            webServer.serve_forever()
        except:
            pass
        webServer.server_close()
        return self.buffer.tobytes()

mp = MinimalMicroProtocolReceive(slice_size=4)
RECEIVE_ADAPTER = ProtocolReceiveAdapterHTTP(microprotocol=mp)
ccreceiver = CCReceiver([], RECEIVE_ADAPTER)
received = ccreceiver.receive()

print(received.decode("utf-8"))
