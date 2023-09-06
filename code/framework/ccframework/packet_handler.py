from abc import ABC
from abc import abstractmethod

from bitstring import Bits, BitArray
from scapy.all import *

from .protocol_adapter import ProtocolReceiveAdapter
from .micro_protocol import TransmissionState

class PacketHandlerSend(ABC):
    '''Interface, das Pakete (z.B. aus Paketmitschnitten oder aus Netfilter-Queue) erhält und
    manipulieren kann.
    '''
    def __init__(self):
        self.send_buffer = list()
    
    def set_send_buffer(self, data: [Bits]):
        '''Speichert Daten, die versendet werden sollen, in einem Puffer in diesem Objekt.
        '''
        self.send_buffer = data

    @abstractmethod
    def handle_packet(self, packet):
        '''Manipuliert das erhaltene Paket, um einen Teil der zu senden Daten darin einzubetten 

        Parameters:
            packet (scapy.packet.Packet): Paket, das verarbeitet werden soll.
                siehe auch https://scapy.readthedocs.io/en/latest/api/scapy.packet.html
        '''
        pass

class PacketHandlerReceive(ABC):
    '''Interface, das Pakete (z.B. aus Paketmitschnitten oder aus Netfilter-Queue) erhält, und daraus
    Daten extrahiert.
    '''
    def __init__(self):
        self.adapter = None

    @abstractmethod
    def handle_packet(self, packet):
        '''Extrahiert daten aus dem übergebenen Paket

        Parameters:
            packet: Paket, das verarbeitet werden soll.
                siehe auch https://scapy.readthedocs.io/en/latest/api/scapy.packet.html
        '''
        pass

class PacketHandlerSendFixedPositionPayload(PacketHandlerSend):
    '''Kann Daten an fest definierten Positionen in UDP- oder TCP-Paketen einbetten.

    Diese Position wird durch ein Offset ab dem Beginn der UDP- bzw. TCP-Payload festgelegt(`start_index`).
    Dadurch werden Daten der Länge `slice_size` beginnend ab dieser Position eingebettet.
    '''
    BYTES = 'bytes'
    BITS = 'bits'
    ALLOWED_UNITS = [BYTES, BITS]

    def __init__(self, start_index: int, slice_size: int, unit='bytes'):
        '''Erstellt einen PacketHandlerSendFixedPositionPayload

        Parameters:
            start_index (int): Position, ab der Daten im UDP- bzw. TCP-Paket ersetzt werden sollen
            slice_size (int): Länge der Daten, die ab `start_index` ersetzt werden sollen
            unit (str): Einheit, in der start_index und slice_size angegeben werden, entweder 'bytes' oder 'bits'
        '''
        assert(unit in self.ALLOWED_UNITS)
        super().__init__()

        if unit == self.BITS:
            self.slice_size = slice_size
            self.start_index = start_index
        elif unit == self.BYTES:
            self.slice_size = slice_size * 8
            self.start_index = start_index * 8

    def handle_packet(self, packet):
        '''Ersetzt Daten in übergebenen UDP bzw- TCP-Paketen entsprechend der Konfiguration

        Das Paket wird nur manipuliert, wenn es sich um ein UDP-Paket handelt. Andere Pakete bleiben
        unverändert.

        Parameters:
            packet: Paket, in dem Daten ersetzt werden sollen.
        '''
        proto = None
        if UDP in packet:
            proto = UDP
        elif TCP in packet:
            proto = TCP
        else:
            return

        bits_to_send = self.send_buffer.pop(0)
        assert len(bits_to_send) == self.slice_size

        print(f"trying to send: {bits_to_send.tobytes()}")

        packet_data_array = BitArray(bytes(packet[proto].payload))
        for i in range(0,self.slice_size):
            packet_data_array[i+self.start_index] = bits_to_send[i]
        full_payload_to_send = packet_data_array.tobytes()
        packet[proto].payload = Raw(full_payload_to_send)

class PacketHandlerReceiveFixedPositionPayload(PacketHandlerReceive):
    '''Kann Daten von fest definierten Positionen in UDP oder TCP-Paketen extrahieren.

    Diese Position wird durch ein Offset ab dem Beginn der UDP- bzw. TCP-Payload festgelegt(`start_index`).
    Dadurch werden Daten der Länge `slice_size` beginnend ab dieser Position extrahiert.
    '''
    BYTES = 'bytes'
    BITS = 'bits'
    ALLOWED_UNITS = [BYTES, BITS]

    def __init__(self, start_index: int, slice_size: int, unit='bytes'):
        '''Erstellt einen PacketHandlerReceiveFixedPositionPayload

        Parameters:
            start_index (int): Position, ab der Daten aus dem UDP- bzw. TCP-Paket extrahiert werden sollen
            slice_size (int): Länge der Daten, die ab `start_index` extrahiert werden sollen
            unit (str): Einheit, in der start_index und slice_size angegeben werden, entweder 'bytes' oder 'bits'
        '''
        assert(unit in self.ALLOWED_UNITS)
        super().__init__()
        if unit == self.BITS:
            self.slice_size = slice_size
            self.start_index = start_index
        elif unit == self.BYTES:
            self.slice_size = slice_size * 8
            self.start_index = start_index * 8

    def handle_packet(self, packet):
        '''Extrahiert Daten aus übergebenen UDP- bzw. TCP-Paketen entsprechend der Konfiguration

        Daten werden nur extrahiert, wenn es sich um ein UDP- bzw. TCP-Paket handelt. Andere Pakete
        werden nicht beachtet.

        Parameters:
            packet: Paket, aus dem Daten extrahiert werden sollen.

        Returns:
            Extrahierte Daten aus diesem Paket
        '''
        proto = None
        if UDP in packet:
            proto = UDP
        elif TCP in packet:
            proto = TCP
        else:
            return

        payload_raw = packet[proto].payload

        payload_bytes = bytes(payload_raw)
        payload_bits = Bits(payload_bytes)
        bits_in = payload_bits[self.start_index:(self.start_index+self.slice_size)]
        print(f"got data={bits_in.tobytes()}")
        return bits_in


class PacketHandlerSendRegexPayload(PacketHandlerSend):
    '''Kann Daten in einem UDP oder TCP-Paket mittels eines regulären Ausdrucks suchen und ersetzen.

    In der UDP- bzw. TCP-Payload wird das erste Vorkommen des übergebenen Ausdrucks durch einen Teil der zu
    übertragenden Daten ersetzt.
    '''

    def __init__(self, regex: str):
        '''Erstellt einen PacketHandlerSendRegexPayload

        Parameters:
            regex: Regulärer Ausdruck, der die Stelle erkennt, an der Daten einzubetten sind.
        '''
        super().__init__()
        self.regex = re.compile(regex)

    def handle_packet(self, packet):
        '''Ersetzt Daten in übergebenen UDP- bzw. TCP-Paketen entsprechend der Konfiguration

        Das Paket wird nur manipuliert, wenn es sich um ein UDP- bzw. TCP-Paket handelt. Andere 
        Pakete bleiben unverändert.

        Parameters:
            packet: Paket, in dem Daten ersetzt werden sollen.
        '''
        proto = None
        if UDP in packet:
            proto = UDP
        elif TCP in packet:
            proto = TCP
        else:
            return

        data_to_send = self.send_buffer.pop(0).tobytes().decode("utf-8")

        payload_bytes = bytes(packet[proto].payload)
        payload_str = payload_bytes.decode("utf-8")

        replaced_payload = self.regex.sub(data_to_send, payload_str, 1)

        full_payload_to_send = replaced_payload.encode("utf-8")
        packet[proto].payload = Raw(full_payload_to_send)

class PacketHandlerReceiveRegexPayload(PacketHandlerReceive):
    '''Kann Daten in einem UDP- oder TCP-Paket mittels eines regulären Ausdrucks extrahieren.

    In der UDPbzw. TCP-Payload wird das erste Vorkommen des übergebenen Ausdrucks als die
    gewünschten zu empfangenen Daten interpretiert.
    '''

    def __init__(self, regex: str):
        '''Erstellt einen PacketHandlerReceiveRegexPayload

        Parameters:
            regex: Regulärer Ausdruck, der die Stelle erkennt, an der Daten einzubetten sind.
        '''
        super().__init__()
        self.regex = re.compile(regex)

    def handle_packet(self, packet):
        '''Extrahiert Daten aus übergebenen UDP- bzw. TCP-Paketen entsprechend der Konfiguration

        Daten werden nur extrahiert, wenn es sich um ein UDP bzw. TCP-Paket handelt. Andere Pakete
        werden nicht beachtet.

        Parameters:
            packet: Paket, aus dem Daten extrahiert werden sollen.

        Returns:
            Extrahierte Daten aus diesem Paket
        '''
        proto = None
        if UDP in packet:
            proto = UDP
        elif TCP in packet:
            proto = TCP
        else:
            return

        print("handling packet")
        
        payload_bytes = bytes(packet[proto].payload)
        payload_str = payload_bytes.decode("utf-8")

        found_str = self.regex.search(payload_str).group(1)
        found_bits = Bits(found_str.encode("utf-8"))

        print(f"got data={found_bits.tobytes()}")
        return found_bits
