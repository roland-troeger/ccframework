# STDIO-Beispiel

Dieses Beispiel demonstriert die Vor- und Nachverarbeitungsmethoden des Frameworks zur
Verschlüsselung mit AES Counter Mode und Kodierung mit Base64.

Dafür nutzt es die Standardein- und Ausgabe der Prozesse, da diese hinreichend ähnlich zu einer
"echten" Netzwerkübertragung, gleichzeitig aber wesentlich weniger komplex sind. 

Anzeige der verschlüsselten und kodierten Daten:
```
$ python sender.py
9Qp8yUPmb0acCpI=
```

Umleitung der Daten an den Empfänger zur Dekodierung und Entschlüsselung:
```
$ python sender.py | python receiver.py
Hello World
```
