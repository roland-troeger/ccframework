# STDIO-Beispiel mit Mikroprotokoll

Dieses Beispiel demonstriert die Funktionsweise des beispielhaften Mikroprotokolls, das das
Framework mitliefert.

Dafür nutzt es die Standardein- und Ausgabe der Prozesse, da diese hinreichend ähnlich zu einer
"echten" Netzwerkübertragung, gleichzeitig aber wesentlich weniger komplex sind. 

Anzeige der kodierten Daten inkl. Simulation von Übertragungen vor und nach den Base64-kodierten
Nachrichten, die den Covert Channel betreffen:
```
$ python sender.py
koala
panda
elefant

SGVs
bG8g
V29y
bGQ=

löwe
tiger
eisbär
```

Umleitung der Daten an den Empfänger zur Dekodierung und Entschlüsselung:
```
$ python sender.py | python receiver.py
Hello World
```
