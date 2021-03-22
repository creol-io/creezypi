# Creol CreezyPi
Creol Creezy Pi - Repository for running a full CreezyPi node on the Creol Network within a commercial building

## Requirements

To be able to run a Creol creezypi device, you will need at a minimum 

1 CreezyPi which consists of:

* Raspberry Pi 3 Model B+ or Raspberry Pi 4
* Kirale USB Dongle (KTDG 102)
* ATX LED DALI Hat 
* 48V Power Supply
* Internet connection to at least 1 node, ethernet (recommended) or wi-fi
* DALI Capable Luminaires up to 64 on ATX DALI 1, or 256 on ATX DALI4

For more info on hardware assembly consult the docs at [Creol Docs](https://creol.readthedocs.io/)

## Building from Source

If you wish to build from source, simply clone the git repository onto a CreezyPi that has been flashed with a standard Raspbian image.
Run the following

```bash
git submodule init
git submodule update

install python3.7
single line

sudo apt-get update -y && sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y && wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz && tar xf Python-3.7.0.tar.xz && cd Python-3.7.0 && ./configure && make -j 4 && sudo make altinstall && cd .. && sudo rm -r Python-3.7.0 && rm Python-3.7.0.tar.xz && sudo apt-get --purge remove build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y && sudo apt-get autoremove -y && sudo apt-get clean

install RPi.GPIO

sudo apt-get install npm
npm install -g truffle
```

## Running

To run the CreezyPi system, run the following

```bash
python3.7 creezypi/creezypi.py
```

From here you'll be prompted with the Creol menu. Type ```start``` to begin the system

For a fuller detail on classes/configs, consult the [Creol Docs](https://creol.readthedocs.io/)

## Cartesi Integration

In it's current form, the CreezyPi software is able to also run a primitive check on signed web3 calls coming from a CreezyPi to ensure 
that messages coming from other nodes in the network are in fact signed by devices that are reporting them. Meaning that nodes that are new or not registered cannot issue tampering messages to the smart contracts that govern the control system.

Current network topology is as designed as below

![Creol-Cartesi Diagram](https://github.com/creol-io/creezypi/blob/main/CreolDiagram.PNG)
