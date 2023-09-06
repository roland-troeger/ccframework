# Beispiel Aktive Übertragung mit HTTP Client/Server

Dieses Beispiel demonstriert die Anbindung externer Bibliotheken über die vom Framework
bereitgestellten Adapter.
Es zeigt die Implementierung eines "Covert Channels" innerhalb von HTTP, der den POST-Body zur
Einbettung der Übertragung nutzt.

## Vorbereitung

Hier sind keine besonderen Vorbereitungen nötig.

## Ausführung

Starten des Empfängers:
```
python receiver.py
```

Starten des Senders
```
python sender.py
```

Nach dem Start des Senders zeigt der Empfänger ein HTTP-Access-Log an. Sobald der Sendeprozess
beendet ist, kann der Empfänger mit `Strg+C` abgebrochen werden. Nun zeigt er die übertragenen
Daten ("Hello World") in der Standardausgabe an.
