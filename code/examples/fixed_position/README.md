# UDP Fixed Position Beispiel

Dieses Beispiel demonstriert die Einbettung eines Covert Channel innerhalb eines Netzwerkprotokolls,
jeweils in den einzelnen Paketen an fester Position beginnen ab dem UDP-Header.

### Vorbereitung

1. netfilter-queue Feature muss inkl. Abhängigkeiten installiert sein, siehe dazu Installations-README
2. notwendige Tools müssen installiert sein: nftables und ncat (je nach Distribution auch im Paket nmap enthalten)

```
# nftables starten (wenn nicht standardmäßig aktiv)
sudo systemctl start nftables

# Regel für Empfänger erstellen
sudo nft add rule inet filter input udp dport <ziel-port> counter queue num 1 bypass

# Regel für Sender erstellen
sudo nft add rule inet filter output udp dport <ziel-port> counter queue num 0 bypass

# Listen-port öffnen
ncat -ulk <ziel-port> --recv-only --exec /bin/echo -o out.txt
```

## Übertragung starten

Empfänger starten
```
$ sudo python receiver.py
```

Sender starten
```
sudo python sender.py
```
Dummy Overt Traffic:
-> muss mehrmals ausgeführt werden, um mehrere Pakete zu simulieren
```
echo "1234567890abcdefg" | nc -uc <receiver-ip> <ziel-port>
```

## Hinweis zu nft-Regeln

Die mit `sudo nft add rule ...` erstellten Regeln müssen an der ersten Position stehen, um
sicherzugehen, dass nicht andere Regeln zu erst auf die relevanten Pakete angewendet werden.

Das kann mit  `sudo nft -a -n list ruleset` überprüft werden.
Hier muss beispielsweise die Regel `udp dport 56565 [...]` direkt unter `type filter hook [...]` stehen:
```
table inet filter { # handle 16
        chain input { # handle 1
                type filter hook input priority 0; policy drop;
                udp dport 56565 counter packets 0 bytes 0 queue flags bypass to 1 # handle 4
                ct state 0x1 drop comment "early drop of invalid connections" # handle 5
                ct state { 0x2, 0x4 } accept comment "allow tracked connections" # handle 7
                iifname "lo" accept comment "allow from loopback" # handle 8
                ip protocol 1 accept comment "allow icmp" # handle 9
                meta l4proto 58 accept comment "allow icmp v6" # handle 10
                tcp dport 22 accept comment "allow sshd" # handle 11
                meta pkttype 0 limit rate 5/second counter packets 0 bytes 0 reject with icmpx 3 # handle 12
                counter packets 2 bytes 108 # handle 13
        }

```

Falls die Regel standardmäßig nicht an der richtigen Stelle eingefügt wird, kann das durch die Angabe
der im Output von `sudo nft -a -n list ruleset` angegebenen Handles beeinflusst werden:

Einfügen nach der Regel mit best. Handle:
`sudo nft add rule inet filter output position <handle> udp [...]`
Einfügen vor der Regel mit best. Handle:
`sudo nft insert rule inet filter output position <handle> udp [...]`
