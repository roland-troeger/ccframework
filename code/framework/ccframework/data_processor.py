from abc import ABC
from abc import abstractmethod

import base64

from Cryptodome.Cipher import AES

class DataPreProcessor(ABC):
    ''' Vorverarbeitung von Daten vor dem Versenden

    Methods:
        preprocess(self, data: bytes)
            Führt die Vorverarbeitung der Daten durch.
    '''
    @abstractmethod
    def preprocess(self, data: bytes) -> bytes:
        pass

class DataPostProcessor(ABC):
    ''' Nachverarbeitung von Daten nach dem Empfangen

    Methods:
        postprocess(self, data: bytes)
            Führt die Nachverarbeitung der Daten durch.
    '''
    @abstractmethod
    def postprocess(self, data: bytes) -> bytes:
        pass

class DataPreProcessorBase64(DataPreProcessor):
    ''' Vorverarbeitung, die dazu genutzt wird, Daten in base64 zu kodieren
    '''
    def preprocess(self, data: bytes) -> bytes:
        '''Nimmt Bytes entgegen und kodiert diese in Base64.
        Parameters:
            data (bytes): Daten, die kodiert werden sollen
        Returns:
            Base64-kodierte Daten
        '''
        return base64.b64encode(data)
    
class DataPostProcessorBase64(DataPostProcessor):
    ''' Nachverarbeitung, die dazu genutzt wird, Daten in base64 zu dekodieren
    '''
    def postprocess(self, data: bytes) -> bytes:
        '''Nimmt Base64-kodierte Daten entgegen und dekodiert diese zu Bytes.
        Parameters:
            data (bytes): Base64-kodierte Daten, die dekodiert werden sollen
        Returns:
            Dekodierte Daten
        '''
        return base64.b64decode(data)

class DataPreProcessorXOR(DataPreProcessor):
    '''Vorverarbeitung, die dazu genutzt wird, Daten mit XOR zu kodieren
    '''
    
    def __init__(self, key: int):
        self.key = key

    def preprocess(self, data: bytes) -> bytes:
        buffer = bytes()
        for b in data:
            b_xored = b ^ self.key
            buffer += b_xored.to_bytes(1,"little")
        return data_xored

class DataPostProcessorXOR(DataPreProcessorXOR):
    '''Nachverarbeitung, die dazu genutzt wird, Daten mit XOR zu dekodieren
    '''
    
    def __init__(self, key: int):
        self.key = key

    def preprocess(self, data: bytes) -> bytes:
        buffer = bytes()
        for b in data:
            b_xored = b ^ self.key
            buffer += b_xored.to_bytes(1,"little")
        return data_xored

class DataPreProcessorAESCTR(DataPreProcessor):
    '''Vorverarbeitung, die dazu genutzt wird, Daten mit AES Counter Mode zu verschlüsseln.

    Dafür wird im Hintergrund pycryptodome eingesetzt:
    https://www.pycryptodome.org/src/cipher/classic#ctr-mode
    '''

    def __init__(self, key: bytes, aes_iv: bytes, aes_nonce: bytes):
        '''Erstellt einen Vorverarbeiter für die Verschlüsselung mit AES Counter Mode
        
        Für Parameter aes_iv bzw. aes_nonce siehe:
        https://www.pycryptodome.org/src/cipher/classic#ctr-mode

        Parameters:
            key (bytes): Schlüssel, der zur Verschlüsselung eingesetzt werden soll
            aes_iv (bytes): initial_value, wie er an pycryptodome übergeben wird
            aes_nonce (bytes): nonce, wie sie an pycryptodome übergeben wird

            len(aes_iv)+len(nonce) == 16
        '''
        if aes_iv == None:
            assert(len(aes_nonce) == 16)
        elif aes_nonce == None:
            assert(len(aes_iv) == 16)
        else:
            assert(len(aes_iv) + len(aes_nonce) == 16)
        self.cipher = AES.new(key, AES.MODE_CTR, initial_value=aes_iv, nonce=aes_nonce)

    def preprocess(self, data: bytes) -> bytes:
        '''Verschlüsselt übergebene Daten mit AES Counter Mode
        Schlüssel und weitere nötige Informationen wurden bereits bei der Initialisierung des Objekts festgelegt.

        Parameters:
            data (bytes): Daten, die verschlüsselt werden sollen
        
        Returns:
            Verschlüsselte Daten
        '''
        return self.cipher.encrypt(data)

class DataPostProcessorAESCTR(DataPostProcessor):

    def __init__(self, key: bytes, aes_iv: bytes, aes_nonce: bytes):
        '''Erstellt einen Nachverarbeiter für die Entschlüsselung mit AES Counter Mode
        
        Für Parameter aes_iv bzw. aes_nonce siehe:
        https://www.pycryptodome.org/src/cipher/classic#ctr-mode

        Parameters:
            key (bytes): Schlüssel, der zur Verschlüsselung eingesetzt werden soll
            aes_iv (bytes): initial_value, wie er an pycryptodome übergeben wird
            aes_nonce (bytes): nonce, wie sie an pycryptodome übergeben wird

            len(aes_iv)+len(nonce) == 16
        '''
        self.cipher = AES.new(key, AES.MODE_CTR, initial_value=aes_iv, nonce=aes_nonce)

    def postprocess(self, data: bytes) -> bytes:
        '''Entschlüsselt übergebene Daten mit AES Counter Mode
        Schlüssel und weitere nötige Informationen wurden bereits bei der Initialisierung des Objekts festgelegt.

        Parameters:
            data (bytes): Daten, die entschlüsselt werden sollen
        
        Returns:
            Entschlüsselte Daten
        '''
        return self.cipher.decrypt(data)
