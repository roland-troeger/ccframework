from .data_processor import DataPreProcessor
from .protocol_adapter import ProtocolSendAdapter

class CCSender:
    '''CCSender (Covert Channel Sender) Übergeordnete Steuerungsklasse für alle Sendeoperationen.

    Erhält alle Vorverarbeitungsmethoden und den Protokoll-Adapter zur Anbindung an das Netzwerkprotokoll.
    '''

    def __init__(self, pre_processors: [DataPreProcessor], protocol_adapter: ProtocolSendAdapter):
        '''Erstellt einen CCsender.

        Parameters:
            pre_processors ([DataPreProcessor]): Vorverarbeitungsmethoden für empfangene Daten
            protocol_adapter (ProtocolReceiverAdapter): Adapter, der Daten in einem Netzwerkprotokoll einbettet
        '''
        self.protocol_adapter = protocol_adapter
        self.pre_processors = pre_processors
    
    def send(self, data_to_send: bytes):
        '''Startet den Versand von Daten.
        
        Zunächst die zu sendenden Daten nacheinander an die Vorverarbeitungsmethoden übergeben, um
        diese für die Übertragung zu kodieren, zu verschlüsseln und sonstige Vorverarbeitungsmethoden
        durchzuführen.

        Anschließend werden diese zum Versand an den Protkolladapter übergeben.
        '''
        data = data_to_send
        for pp in self.pre_processors:
            data = pp.preprocess(data)
        self.protocol_adapter.send(data)