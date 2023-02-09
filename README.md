# MyBeaconChain


╔═╗╔═╗───╔══╗───────────────╔═══╦╗
║║╚╝║║───║╔╗║───────────────║╔═╗║║
║╔╗╔╗╠╗─╔╣╚╝╚╦══╦══╦══╦══╦═╗║║─╚╣╚═╦══╦╦═╗
║║║║║║║─║║╔═╗║║═╣╔╗║╔═╣╔╗║╔╗╣║─╔╣╔╗║╔╗╠╣╔╗╗
║║║║║║╚═╝║╚═╝║║═╣╔╗║╚═╣╚╝║║║║╚═╝║║║║╔╗║║║║║
╚╝╚╝╚╩═╗╔╩═══╩══╩╝╚╩══╩══╩╝╚╩═══╩╝╚╩╝╚╩╩╝╚╝
─────╔═╝║
─────╚══╝

Beacon Chain from scratch, written in Python.  Based on [The Beacon Chain Ethereum 2.0 explainer you need to read first](https://ethos.dev/beacon-chain)


### Setup

```sh
git clone git@github.com:devtooligan/MyBeaconChain.git
cd MyBeaconChain
```


### Usage
```sh
python3 src/main.py
```

_The script will process one epoch.  Hit enter to process another._

Features complete:

- [x] Proposers selected randomly weighted by ETH balance
- [x] Committees formed for each slot
- [x] Proposals solicited
- [x] LMD_GHOST and FFG votes solicited and tallied for each slot
- [x] Blocks attested
- [x] Checkpoints justified
- [x] Checkpoints finalized
- [ ] Rewards distributed