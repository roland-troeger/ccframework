# Covert Storage Channel Framework

## Basis-Installation

```
# python virtual environment erstellen
python -m venv .venv

# python virtual environment aktivieren
source .venv/bin/activate

# Installation im virtual environment (editable mode)
pip install -e framework
```

## Install netfilter-queue Feature

```
# installation native dependencies - debian
apt-get install build-essential python3-dev libnetfilter-queue-dev

# installation native dependencies - arch linux
pacman -Syu libnetfilter_queue

# installation netfilter-queue feature
pip install -e framework[netfilter-queue]
```
