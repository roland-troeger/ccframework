from setuptools import setup
  
setup(
    name='ccframework',
    version='0.2.0',
    description='Covert Channel Framework',
    author='Roland Tröger',
    author_email='roland.troeger@mailbox.org',
    packages=['ccframework'],
    install_requires=['scapy', 'pycryptodomex', 'bitstring'],
    extras_require = {
        'netfilter-queue': ['netfilterqueue']
    }
)
