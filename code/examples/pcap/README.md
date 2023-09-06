# Beispiel Paketmitschnitt

Dieses Beispiel demonstriert die Funktionen zum aktiven Senden bzw. passiven Empfangen aus einem
Paketmitschnitt.

## Senden

Die Übertragung kann mit folgendem Befehl gestartet werden:
```
sudo python sender.py
```
Währenddessen kann die Übertragung z.B. mittels Wireshark mitgeschnitten werden. Der daraus
resultierende Mitschnitt kann (nach Filterung auf die relevanten Pakete) für den Empfänger
eingesetzt werden.

## Verfizierung durch Analyse des Paketmitschnittes

Dass die Daten erfolgreich in die zu sendenden Pakete eingebettet werden, kann mithilfe eines
weiteren Paketmitschnittes nachgewiesen werden. Nutzt man Wireshark zur Aufzeichnung von
Traffic auf allen Interfaces und filtert die Übertragung mittels `udp.port == 56565`, sind die Daten
in den jeweils ersten 4 Bytes der Payload enthalten - inklusive der NUllbytes als Zeichen zum Start 
und zum Ende der Übertragung, die durch das minimalistische Mikroprotokoll eingefügt werden.

## Indirektes Empfangen aus Paketmitschnitt

```
python receiver.py
```

## Quelle des Paketmitschnitts
https://wiki.wireshark.org/SampleCaptures#sample-captures
-> dns.cap (libpcap) Various DNS lookups

-> Nachträglich gefiltert auf Pakete mit DNS Query Requests
-> gespeichert in dns_requests.pcap
