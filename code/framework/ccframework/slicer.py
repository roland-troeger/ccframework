from abc import ABC, abstractmethod
from bitstring import Bits, ConstBitStream, ReadError

class BitSlicer(ABC):
    '''Interface, das zur Zerteilung von Bits-Objekte (`bitstring`) genutzt werden kann.
    Implementiert standardmäßig durch `SimpleBitSlicer`, kann aber bei Bedarf auch durch komplexere
    Algorithmen ausgetauscht werden, beispielsweise um variable Längen der einzelnen Teile zu 
    ermöglichen.

    Methods:
        slice(self, data: Bits):
            Teilt Daten in kleine Stücke auf. 
    '''
    @abstractmethod
    def slice(self, data: Bits) -> [Bits]:
        '''Teilt ein Bits-Objekt in ein Array von Bits-Objekten auf.
        
        Parameters:
            data: Daten, die in Stücke aufgeteilt werden sollen

        Returns:
            aufgeteilte Daten
        '''
        pass

class SimpleBitSlicer(BitSlicer):
    ''' Klasse, die dazu dient Objekte des Typs Bits (aus `bitstring`) in Stücke fester Länge zu zerteilen.

    Attributes:
        slice_size: int
            Länge der Stücke, in die die Daten aufgeteilt werden sollen.
        padding: Bits
            Padding, das am Ende der Aufteilung an das letzte Stück angehängt werden soll, sofern dieses kleiner als slice_size ist.
    '''

    def __init__(self, slice_size: int, padding: Bits=None):
        '''Erstellt einen SimpleBitSlicer.
        Parameters:
            slice_size (int): Länge der einzelnen Stücke
                `slice_size > 0`
            padding: (Bits): Padding, das an die letzten Bits angehängt wird, sofern diese nicht so lang sind wie slice_size
                `len(padding) >= slice_size-1`
        '''
        assert(slice_size > 0)
        assert(padding is not None)
        assert(len(padding) >= (slice_size-1))
        assert(type(padding) == Bits)
        self.slice_size = slice_size
        self.padding = padding
    
    def slice(self, data: Bits) -> [Bits]:
        ''' Zerteilt `data` in Stücke der Länge `self.slice_size`.
        Wenn `len(data)` kein ganzzahliges Vielfaches der `self.slice_size` ist, also am Ende der
        Aufteilung noch eine Anzahl Bytes übrig bleibt, die kleiner als `self.slice_size` ist, wird
        daran noch ein entsprechendes Padding angehängt.

        Beispiel: 
        Zerteilt man `00110` bei einer `slice_size` von `3` und einem Padding von `100`, erhält man `['001', '101']`

        Parameters:
            data (Bits): Daten, die in kleinere Stücke zerteilt werden sollen
        Returns:
            zerteilte Daten, die ggf. mit Padding auf gleich lange Stücke aufgefüllt wurden.
        '''
        buf = ConstBitStream(data)
        slices = list()
        while True:
            try:
                bitstream_part = buf.read(f"bits{self.slice_size}")
                slices.append(bitstream_part)
            except ReadError as e:
                rest = buf.read('bits')
                if len(rest) > 0:
                    pad_length = self.slice_size-len(rest)
                    pad = self.padding[:pad_length]
                    slices.append(rest+pad)
                break
        return slices
