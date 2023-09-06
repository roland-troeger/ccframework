from abc import ABC
from abc import abstractmethod
import enum
from bitstring import Bits

from .slicer import SimpleBitSlicer

class TransmissionState(enum.Enum):
    '''Klasse, die Zustand einer Übertragung repräsentiert.
    '''
    # Übertragung hat noch nicht begonnen
    WAITING_FOR_TRANSMISSION = enum.auto()
    # Übertragung ist aktuell aktiv
    ACTIVE_TRANSMISSION = enum.auto()
    # Übertragung ist bereits beendet
    FINISHED_TRANSMISSION = enum.auto()
    
class MicroProtocolResponse:
    ''' Fasst Rückgabewerte bei Empfang mit einem Mikroprotokoll zu einem einzelnen Objekt zusammen,
    um sie leichter als Returnwert nutzen zu können.
    Diese Rückgabewerte bestehen aus Zustand der Übertragung und, sofern vorhanden, den empfangenen Daten.
    '''
    def __init__(self, transmission_state: TransmissionState, data: bytes=None):
        self.transmission_state = transmission_state
        self.data = data

class MicroProtocolSend(ABC):
    ''' Mikroprotokoll für den Versand von Daten
    
    Bei Versand bereitet dieses die Daten so vor, dass der Empfänger Start und Ende einer
    Übertragung erkennen kann. 

    Je nach Bedarf können auch weitere Funktionen eines Mikroprotokolls implementiert werden.
    '''
    @abstractmethod
    def preprocess(self, data: Bits) -> [Bits]:
        ''' Bereitet Daten auf den Versand vor

        Parameters:
            data (Bits): Daten, die zum Versand vorbereitet werden sollen
        
        Returns:
            Versandbereite Daten inkl. Metainformationen, die das Mikroprotokoll hinzufügt, um seine
            Funktionen umzusetzen.
        '''
        pass

class MicroProtocolReceive(ABC):
    ''' Mikroprotokoll für den Empfang von Daten
    
    Bei Empfang wertet das Mikroprotokoll die empfangenen Daten aus und stellt fest, in welchem
    Zustand sich die Übertragung befindet (`TransmissionState`) und liefert diese Informationen 
    weiter.

    Je nach Bedarf können auch weitere Funktionen eines Mikroprotokolls implementiert werden.
    '''
    @abstractmethod
    def postprocess(self, data: Bits) -> MicroProtocolResponse:
        ''' Wertet Daten nach Empfang aus, um Funktionen des Mikroprotokolls umzusetzen, z.B.
        Erkenung von Start und Ende der Übertragung.

        Wird vom ProtocolAdapter für alle empfangenen Daten aufgerufen, um Metainformationen des
        Mikroprotokolls auszuwerten und dessen Funktionen umzusetzen.

        Parameters:
            data (Bits): Daten, die empfangen wurden.

        Returns:
            MicroProtocolResponse, die Zustand der Übertragung und eventuell empfangene Daten beinhaltet
        '''
        pass

class MinimalMicroProtocolSend(MicroProtocolSend):
    ''' Minimalistisches Mikroprotokoll, das lediglich Start und Ende einer Übertragung festellen kann.

    Das wird durch Senden von Null-Bytes bzw. -Bits jeweils vor und nach der Übertragung der Nutzdaten
    implementiert.
    Dieses Mikroprotokoll ist dadurch ggf. nur in bestimmten Use-Cases einsetzbar. Es dient vielmehr
    der Demonstration, wie ein Funktionen eines Mikroprotokolls im Kontext dieses Frameworks
    implementiert werden können.
    '''
    BYTES = 'bytes'
    BITS = 'bits'
    ALLOWED_UNITS = [BYTES, BITS]

    def __init__(self, slice_size: int, unit='bytes', padding: Bits=None):
        '''Erstellt ein MinimalMicroProtocolSend

        Parameters:
            slice_size (int): Länge der Stücke, in die die zu versendenden Daten aufgeteilt werden sollen
            unit (str): Einheit, in der `slice_size` angegeben wurde, entweder 'bytes' oder 'bits'
            padding (Bits): Padding, das bei der Zerteilung der Daten durch `SimpleBitSlicer` an zu 
                kleine Stücke angehängt werden soll, um diese auf `slice_size` zu verlängern.
        '''
        assert(unit in self.ALLOWED_UNITS)
        if unit == self.BITS:
            self.slice_size = slice_size
        elif unit == self.BYTES:
            self.slice_size = slice_size * 8
        self.slicer = SimpleBitSlicer(slice_size=self.slice_size, padding=padding)

    def preprocess(self, data: Bits) -> [Bits]:
        '''Vorbereitung der Daten zum Versand.

        Zerteilt die Daten in Stücke mit der Länge `slice_size` (Einheit abhängig von der Angabe im Konstruktor).
        Zusätzlich werden Null-Bytes bzw. -Bits angehängt, die dem Empfänger zur Erkennung von
        Start und Ende der Übertragung dienen.

        So wird aus `00110` bei `slice_slice` von `3` in `bits` und einem Padding von `000`:
        `['000','001','100','000']`

        Parameters:
            data (Bits): Daten, die versendet werden sollen.
        Returns:
            Vorbereitete Daten, die durch den ProtocolAdapter versendet werden können.
        '''
        assert(type(data) == Bits)

        data_to_send = list()
        zero_bits = Bits('0b' + '0'*self.slice_size)
        data_to_send.append(zero_bits)
        data_to_send += self.slicer.slice(data)
        data_to_send.append(zero_bits)
        return data_to_send


class MinimalMicroProtocolReceive(MicroProtocolReceive):
    ''' Minimalistisches Mikroprotokoll, das lediglich Start und Ende einer Übertragung festellen kann.

    Das wird durch Senden von Null-Bytes bzw. -Bits jeweils vor und nach der Übertragung der Nutzdaten
    implementiert.
    Dieses Mikroprotokoll ist dadurch ggf. nur in bestimmten Use-Cases einsetzbar. Es dient vielmehr
    der Demonstration, wie ein Funktionen eines Mikroprotokolls im Kontext dieses Frameworks
    implementiert werden können.
    '''
    BYTES = 'bytes'
    BITS = 'bits'
    ALLOWED_UNITS = [BYTES, BITS]

    def __init__(self, slice_size: int, unit='bytes'):
        '''Erstellt ein MinimalMicroProtocolReceive

        Parameters:
            slice_size (int): Länge der Stücke, in die die zu versendenden Daten aufgeteilt werden sollen
            unit (str): Einheit, in der `slice_size` angegeben wurde, entweder 'bytes' oder 'bits'
        '''
        assert(unit in self.ALLOWED_UNITS)
        self.transmission_state = TransmissionState.WAITING_FOR_TRANSMISSION
        if unit == self.BITS:
            self.slice_size = slice_size
        elif unit == self.BYTES:
            self.slice_size = slice_size * 8

    def postprocess(self, data: Bits) -> MicroProtocolResponse:
        '''Verarbeitung von Empfangenen Daten.
        Wird vom ProtocolAdapter für alle empfangenen Daten aufgerufen, um Metainformationen des 
        Mikroprotokolls auszuwerten und dessen Funktionen umzusetzen, hier Erkennung von Start und 
        Ende der Übertragung.

        Hier wird der Start bzw. Ende einer Übertragung erkannt, wenn alle in `data` enthaltenen Bits
        `0` sind. 
        Die nach dem Start und vor dem Ende der Übertragung erhaltenen Bits in `data` entsprechen
        zusammen den eigentlichen Nutzdaten.

        Parameters:
            data (Bits): vom ProtocolAdapter aus der Übertragung extrahierte Daten, die ausgewertet
                werden sollen.
        Returns:
            MicroProtocolResponse, die Zustand der Übertragung und evtl. empfangene Daten enthält.
        '''
        assert(type(data) == Bits)

        zero_bits = Bits('0b' + '0'*self.slice_size)
        transmission_data = None
        if self.transmission_state is TransmissionState.WAITING_FOR_TRANSMISSION:
            if data == zero_bits:
                self.transmission_state = TransmissionState.ACTIVE_TRANSMISSION
        elif self.transmission_state is TransmissionState.ACTIVE_TRANSMISSION:
            if data == zero_bits:
                self.transmission_state = TransmissionState.FINISHED_TRANSMISSION
            else:
                transmission_data = data
        elif self.transmission_state is TransmissionState.FINISHED_TRANSMISSION:
                pass
        else:
            raise Exception(f"Unexpected transmission_state: {self.transmission_state}")
        return MicroProtocolResponse(self.transmission_state, transmission_data)
