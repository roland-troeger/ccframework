from .data_processor import DataPostProcessor
from .protocol_adapter import ProtocolReceiveAdapter

class CCReceiver:
    '''CCReceiver (Covert Channel Receiver) Übergeordnete Steuerungsklasse für alle Empfangsoperationen.

    Erhält alle Nachverarbeitungsmethoden und den Protokoll-Adapter zur Anbindung an das Netzwerkprotokoll.
    '''

    def __init__(self, post_processors: [DataPostProcessor], protocol_adapter: ProtocolReceiveAdapter):
        '''Erstellt einen CCReceiver.

        Parameters:
            post_processors ([DataPostProcessor]): Nachverarbeitungsmethoden für empfangene Daten
            protocol_adapter (ProtocolReceiverAdapter): Adapter, der Daten aus einem Netzwerkprotokoll extrahiert
        '''
        self.protocol_adapter = protocol_adapter
        self.post_processors = post_processors
    
    def receive(self) -> bytes:
        '''Startet den Empfang von Daten und liefert diese zurück
        
        Nachdem der Protokolladapter Daten empfangen und zurückgeliefert hat, werden diese 
        nacheinander an die Nachverarbeitungsmethoden gegeben, um sie zu dekodieren, zu entschlüsseln
        oder sonstige Verarbeitungsmethoden durchzuführen.
        '''
        data = self.protocol_adapter.receive()
        for pp in self.post_processors:
            data = pp.postprocess(data)
        return data