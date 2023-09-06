from .micro_protocol import MicroProtocolSend, MicroProtocolReceive
from .protocol_adapter import ProtocolSendAdapter, ProtocolReceiveAdapter
from .packet_handler import PacketHandlerSend, PacketHandlerReceive

from bitstring import Bits
from scapy.all import *
from scapy.utils import rdpcap
import itertools

class ProtocolSendAdapterPCAP(ProtocolSendAdapter):
    '''Adapter, der Pakete aus einem Paketmitschnitt versenden kann

    Dafür ist neben einigen Angaben, die in diesen Paketen geändert werden müssen, um nicht
    von Anti-Spoofing-Maßnahmen verworfen zu werden, auch ein PacketHandlerSend nötig, der die
    Daten in dem Paket einbettet.
    '''
    
    def __init__(self, pcap_file_path: str, 
                    new_src_ip: str=None, 
                    new_dst_ip: str=None, 
                    new_src_mac: str=None, 
                    new_dst_mac: str=None,
                    new_src_port: int=None,
                    new_dst_port: int=None,
                    packet_handler: PacketHandlerSend=None, 
                    microprotocol: MicroProtocolSend=None):
        '''Erstellt einen ProtocolSendAdapterPCAP
        
        Parameters:
            pcap_file_path (str): Pfad zum Paketmitschnitt, aus dem die zu versendenden Pakete ausgelesen werden
            new_src_ip (str): Quell-IP-Adresse, die in den Paketen eingetragen werden soll
            new_dst_ip (str): Ziel-IP-Adresse, die in den Paketen eingetragen werden soll
            new_src_mac (str): Quell-MAC-Adresse, die in den Paketen eingetragen werden soll
            new_dst_mac (str): Ziel-MAC-Adresse, die in den Paketen eingetragen werden soll
            new_src_port (str): Quell-Port, der in den Paketen eingetragen werden soll
            new_dst_port (str): Ziel-Port, der in den Paketen eingetragen werden soll
            packet_handler (PacketHandlerSend): Methode zur Einbettung der Daten in die Pakete
            microprotocol (MicroProtocolSend): Mikroprotokoll, das zur Vorbereitung der Daten genutzt werden soll (optional)
        '''
        assert(packet_handler is not None)
        self.packet_handler = packet_handler
        self.microprotocol = microprotocol
        self.pcap_packets = rdpcap(pcap_file_path)

        self.new_src_mac = new_src_mac
        self.new_dst_mac = new_dst_mac

        self.new_src_ip = new_src_ip
        self.new_dst_ip = new_dst_ip

        self.new_src_port = new_src_port
        self.new_dst_port = new_dst_port
    
    def send(self, data: bytes):
        '''Nimmt Daten zum Versand entgegen und startet die Methoden, die zum Versand der Pakete nötig sind
        Die aus dieser Queue erhaltenen Pakete werden durch jeweils einzelne Aufrufe von self.handle_packet() verarbeitet.

        Sollten weniger Pakete im Paketmitschnitt enthalten sein, als nötig sind um die gewünschten
        Daten zu versenden, werden die Pakete auch mehrfach verwendet.

        Parameters:
            data (bytes): Daten, die versendet werden
        '''
        transmission_data = Bits(data)
        if self.microprotocol != None:
            transmission_data = self.microprotocol.preprocess(transmission_data)
        if type(transmission_data) == Bits:
            transmission_data = [transmission_data]
        self.packet_handler.set_send_buffer(transmission_data)

        for packet in itertools.cycle(self.pcap_packets):
            self.handle_packet(packet)
            if len(self.packet_handler.send_buffer) == 0:
                break
    
    def handle_packet(self, packet):
        '''Manipuliert die Pakete und versendet diese schließlich.

        Zunächst wird das Paket an den PacketHandlerSend übergeben, der bei der Erstellung
        des Adapters übergeben wurde. Dieser bettet die zu sendenden Daten im Paket ein.

        Anschließend werden die Quell- und Ziel-Adressen, Ports und Metadaten des Pakets angepasst, 
        es glaubwürdig erscheinen zu lassen.

        Zuletzt wird das Paket tatsächlich versendet.

        Parameters:
            packet: Paket, das verarbeitet werden soll.
        '''
        self.packet_handler.handle_packet(packet)

        if self.new_src_mac != None:
            packet[Ether].src = self.new_src_mac
        if self.new_dst_mac != None:
            packet[Ether].dst = self.new_dst_mac

        if UDP in packet:
            if self.new_src_port != None:
                packet[UDP].sport = self.new_src_port
            if self.new_dst_port != None:
                packet[UDP].dport = self.new_dst_port
            del packet[UDP].len
            del packet[UDP].chksum
        if TCP in packet:
            if self.new_src_port != None:
                packet[TCP].sport = self.new_src_port
            if self.new_dst_port != None:
                packet[TCP].dport = self.new_dst_port
            del packet[TCP].len
            del packet[TCP].chksum

        if IP in packet:
            if self.new_src_ip != None:
                packet[IP].src = self.new_src_ip
            if self.new_dst_ip != None:
                packet[IP].dst = self.new_dst_ip
            del packet[IP].len
            del packet[IP].chksum
        sendp(packet)


class ProtocolReceiveAdapterPCAP(ProtocolReceiveAdapter):
    '''Adapter, der Daten aus bereits vorliegenden Paketmitschnitt-Dateien extrahieren kann.
    '''
    def __init__(self, pcap_file_path: str, packet_handler: PacketHandlerReceive=None, microprotocol: MicroProtocolReceive=None):
        '''Erstellt einen ProtocolReceiveAdapterPCAP
        
        Parameters: 
            pcap_file_path (str): Pfad zum Paketmitschnitt im Dateisystem
            packet_handler (PacketHandlerReceive): Methode zur Extraktion der Daten aus den Paketen
            microprotocol (MicroProtocolReceive): Mikroprotokoll, das zur Nachverarbeitung der Daten genutzt werden soll (optional)
        '''
        assert(packet_handler is not None)
        super().__init__(microprotocol=microprotocol)
        self.packet_handler = packet_handler
        self.pcap_file_path = pcap_file_path

    def receive(self) -> bytes:
        '''Empfängt Daten aus einem Paketmitschnitt und liefert diese zurück.

        Zunächst wird der Paketmitschnitt ausgelesen und die enthaltenen Pakete anschließend 
        nacheinander an den PacketHandlerReceive übergeben, der die relevanten Daten ausliest und
        zurückgibt.
        '''
        pcap_packets = rdpcap(self.pcap_file_path)
        for packet in pcap_packets:
            data = self.packet_handler.handle_packet(packet)
            self.handle_received_data(data)
        tmp_buf = self.buffer
        self.buffer = Bits()
        return tmp_buf.tobytes()
