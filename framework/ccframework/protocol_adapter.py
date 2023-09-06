from abc import ABC
from abc import abstractmethod
import fileinput

from bitstring import Bits
from scapy.all import *

from .micro_protocol import MicroProtocolSend, MicroProtocolReceive, TransmissionState

class ProtocolSendAdapter(ABC):
    '''Adapter zum Senden von Daten mit beliebigen Protokollen'''

    def __init__(self, microprotocol: MicroProtocolSend=None):
        '''Erstellt einen ProtocolSendAdapter
        
        Parameters:
            microprotocol: Mikroprotokoll, das genutzt werden soll (optional)
        '''
        self.microprotocol = microprotocol

    @abstractmethod
    def send(self, data: bytes):
        '''Sendet übergebene Daten'''
        pass
    
class ProtocolReceiveAdapter(ABC):
    '''Adapter zum Empfangen von Daten mit beliebigen Protokollen'''

    def __init__(self, microprotocol: MicroProtocolReceive=None):
        '''Erstellt einen ProtocolReceiveAdapter
        
        Parameters:
            microprotocol: Mikroprotokoll, das genutzt werden soll (optional)
        '''
        self.buffer = Bits()
        self.microprotocol = microprotocol

    @abstractmethod
    def receive(self) -> bytes:
        '''Empfängt Daten und liefert diese zurück'''
        pass

    def handle_received_data(self, data: Bits):
        '''Verarbeitet vom Mikroprotokoll übergebene Daten abhängig vom Übertragungszustand und
        speichert diese im Empfangspuffer
        '''
        if self.microprotocol != None:
            resp = self.microprotocol.postprocess(data)
            if resp.transmission_state is TransmissionState.WAITING_FOR_TRANSMISSION:
                pass
            elif resp.transmission_state is TransmissionState.ACTIVE_TRANSMISSION:
                if resp.data != None:
                    self.buffer += resp.data
            elif resp.transmission_state is TransmissionState.FINISHED_TRANSMISSION:
                pass
            else:
                raise Exception(f"Unexpected transmission_state: {self.transmission_state}")
        else:
            self.buffer += data
        
# Intended for Debugging and Demonstration Purposes
class ProtocolSendAdapterStdio(ProtocolSendAdapter):
    '''Adapter, der zu senden Daten auf der Standardausgabe ausgibt'''

    def __init__(self, microprotocol: MicroProtocolSend=None):
        super().__init__(microprotocol)

    def send(self, data: bytes):
        '''Gibt zu senden Daten auf der Standardausgabe aus. 
        Diese Daten werden bei Bedarf an ein Mikroprotokoll zur Vorbereitung übergeben.
        '''
        transmission_data = Bits(data)
        if self.microprotocol != None:
            transmission_data = self.microprotocol.preprocess(transmission_data)
        if type(transmission_data) == Bits:
            transmission_data = [transmission_data]
        for some_bits in transmission_data:
            print(some_bits.tobytes().decode("utf-8"))

class ProtocolReceiveAdapterStdio(ProtocolReceiveAdapter):
    '''Adapter, der Daten von der Standardeingabe einliest'''

    def __init__(self, microprotocol: MicroProtocolReceive=None):
        super().__init__(microprotocol)

    def receive(self) -> bytes:
        '''Liest Daten von der Standardeingabe bis zum Ende der Eingabe'''
        for line in fileinput.input():
            line_bytes = line.encode("utf-8").rstrip()
            self.handle_received_data(Bits(line_bytes))
        return self.buffer.tobytes()
