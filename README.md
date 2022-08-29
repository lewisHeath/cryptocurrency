# My own cryptocurrency

This is the repo for the cryptocurrency I built from scratch using python with flask.

## Installation

Method 1 - Clone from repo and replicate environment using conda

```bash
git clone https://github.com/lewisHeath/cryptocurrency
cd cryptocurrency
conda-env create -n blockchain -f= blockchain.yml
conda activate blockchain
```
Method 2 - Run using executable file  
<a href="https://github.com/lewisHeath/cryptocurrency/cryptocurrency" download>Download</a>
## Usage
If you used method 1. Make sure you are in the cryptocurrency directory and run
```bash
python3 Main.py
python3 Main.py --port xxxx --ip xxx.xxx.xxx.xxx
```
The ports on your router must be forwarded correctly or have the router in bridged mode or you will not correctly connect to the network.
