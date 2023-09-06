from .micro_protocol import MicroProtocolSend, MicroProtocolReceive, TransmissionState
from .packet_handler import PacketHandlerSend, PacketHandlerReceive
from .protocol_adapter import ProtocolSendAdapter, ProtocolReceiveAdapter

from abc import abstractmethod
from bitstring import Bits
from netfilterqueue import NetfilterQueue
from scapy.all import *

class ProtocolSendAdapterNFQ(ProtocolSendAdapter):
    '''Adapter, der Daten mit der Linux-Kernel-Funktion Netfilter-Queue senden kann.

    Dafür wird ein entsprechender PacketHandlerSend benötigt, der die Pakete zur Einbettung der
    Daten manipuliert.
    '''

    def __init__(self, queue_id: int, packet_handler: PacketHandlerSend=None, microprotocol: MicroProtocolSend=None):
        '''Erstellt einen ProtocolSendAdapterNFQ

        Parameters:
            queue_id (int): ID der Netfilter-Queue, die zum Senden der Daten genutzt werden soll.
            packet_handler (PacketHandlerSend): Methode zur Einbettung der Daten in die Pakete
            microprotocol (MicroProtocolSend): Mikroprotokoll, das zur Vorbereitung der Daten genutzt werden soll (optional)
        '''
        assert(packet_handler is not None)
        self.packet_handler = packet_handler
        self.queue_id = queue_id
        self.microprotocol = microprotocol

    def send(self, data: bytes):
        '''Nimmt Daten zum Versand entgegen und startet die Methoden, die die Netfilter-Queue bearbeiten.
        Die aus dieser Queue erhaltenen Pakete werden durch jeweils einzelne Aufrufe von self.handle_packet() verarbeitet.

        Parameters:
            data (bytes): Daten, die versendet werden
        '''
        transmission_data = Bits(data)
        if self.microprotocol != None:
            transmission_data = self.microprotocol.preprocess(transmission_data)
        if type(transmission_data) == Bits:
            transmission_data = [transmission_data]
        self.packet_handler.set_send_buffer(transmission_data)

        nfqueue = NetfilterQueue()
        nfqueue.bind(self.queue_id, self.handle_packet)
        try:
            nfqueue.run()
        except Exception as e:
            print(e)
        nfqueue.unbind()

    def handle_packet(self, packet):
        '''Verarbeitet einzelne, aus der Netfilter-Queue erhaltene, Pakete
        Diese werden an den PacketHandlerSend, der bei der Erstellung des Adapters angegeben wurde,
        übergeben und dort manipuliert.
        Anschließend werden hier einige Metadaten der Pakete neu berechnet, damit die Pakete auch
        nach Manipulation noch gültig sind (insb. Längenangaben und Prüfsummen).

        Wird hier festgestellt, dass alle Daten versendet wurden, wird eine Exception ausgelöst,
        wodurch die Verarbeitung der Pakete aus der Netfilter-Queue beendet wird.

        Parameters:
            packet: Paket, das verarbeitet werden soll
        '''
        packet.retain() # keep copy of payload after .get_payload
        payload_bytes = packet.get_payload() # raw bytes starting with IP header
        parsed_packet = IP(payload_bytes) # scapy object

        self.packet_handler.handle_packet(parsed_packet)

        if IP in parsed_packet:
            del parsed_packet[IP].len
            del parsed_packet[IP].chksum
        if UDP in parsed_packet:
            del parsed_packet[UDP].len
            del parsed_packet[UDP].chksum
        if TCP in parsed_packet:
            del parsed_packet[TCP].len
            del parsed_packet[TCP].chksum

        packet_payload_to_send = parsed_packet.build()
        packet.set_payload(packet_payload_to_send)
        packet.accept()

        if len(self.packet_handler.send_buffer) == 0:
            raise Exception("done sending")

class ProtocolReceiveAdapterNFQ(ProtocolReceiveAdapter):
    '''Adapter, der Daten mit der Linux-Kernel-Funktion Netfilter-Queue empfangen kann.

    Dafür wird ein entsprechender PacketHandlerReceive benötigt, der die Pakete zur Extraktion der
    Daten auswerten kann.
    '''

    def __init__(self, queue_id: int, packet_handler: PacketHandlerReceive=None, microprotocol: MicroProtocolReceive=None):
        '''Erstellt einen ProtocolReceiveAdapterNFQ

        Parameters:
            queue_id (int): ID der Netfilter-Queue, die zum Empfangen der Daten genutzt werden soll.
            packet_handler (PacketHandlerReceive): Methode zur Extraktion der Daten aus den Paketen
            microprotocol (MicroProtocolReceive): Mikroprotokoll, das zur Nachverarbeitung der Daten genutzt werden soll (optional)
        '''
        assert(packet_handler is not None)
        super().__init__(microprotocol=microprotocol)
        self.packet_handler = packet_handler
        self.queue_id = queue_id

    def receive(self) -> bytes:
        '''Empfängt Daten aus Paketen aus einer Netfilter-Queue und liefert diese Daten zurück. 

        Dafür werden zunächst die nötigen Methoden zur Verarbeitung von Paketen aus der
        Netfilter-Queue gestartet.
        Die aus dieser Queue erhaltenen Pakete werden durch jeweils einzelne Aufrufe von self.handle_packet() verarbeitet.

        Returns:
            Empfangene Daten
        '''
        nfqueue = NetfilterQueue()
        nfqueue.bind(self.queue_id, self.handle_packet)
        try:
            nfqueue.run()
        except Exception as e:
            print(e)
        nfqueue.unbind()
        tmp_buf = self.buffer
        self.buffer = Bits()
        return tmp_buf.tobytes()

    def handle_packet(self, packet):
        '''Verarbeitet einzelne, aus der Netfilter-Queue erhaltene, Pakete
        Diese werden an den PacketHandlerReceive, der bei der Erstellung des Adapters angegeben wurde,
        übergeben und dort ausgewertet.
        Wird hier festgestellt, dass die Übertragung beendet ist, wird eine Exception ausgelöst,
        wodurch die Verarbeitung der Pakete aus der Netfilter-Queue beendet wird.

        Parameters:
            packet: Paket, das verarbeitet werden soll
        '''
        packet.retain() # keep copy of payload after .get_payload
        payload_bytes = packet.get_payload() # raw bytes starting with IP header
        parsed_packet = IP(payload_bytes) # scapy object

        data = self.packet_handler.handle_packet(parsed_packet)
        self.handle_received_data(data)

        packet.accept()
        
        if self.microprotocol.transmission_state == TransmissionState.FINISHED_TRANSMISSION:
            raise Exception("transmission finished")
