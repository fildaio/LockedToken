# Locked token

Vyper contracts used for linear release token.

## Overview

## Testing and Development

### Dependencies

- [python3](https://www.python.org/downloads/release/python-368/) version 3.6 or greater, python3-dev
- [vyper](https://github.com/vyperlang/vyper) version [0.2.12](https://github.com/vyperlang/vyper/releases/tag/v0.2.12)
- [brownie](https://github.com/iamdefinitelyahuman/brownie) - tested with version [1.14.6](https://github.com/eth-brownie/brownie/releases/tag/v1.14.6)
- [brownie-token-tester](https://github.com/iamdefinitelyahuman/brownie-token-tester) - tested with version [0.2.2](https://github.com/iamdefinitelyahuman/brownie-token-tester/releases/tag/v0.2.2)
- [ganache-cli](https://github.com/trufflesuite/ganache-cli) - tested with version [6.12.1](https://github.com/trufflesuite/ganache-cli/releases/tag/v6.12.1)

### Setup

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html). Next, clone the repo and install the developer dependencies:

```bash
git clone https://github.com/fildaio/LockedToken.git
cd LockedToken
pip install -r requirements.txt
```

### Running the Tests

The test suite is split between [unit](tests/unitary) and [integration](tests/integration) tests. To run the entire suite:

```bash
brownie test
```

To run only the unit tests or integration tests:

```bash
brownie test tests/unitary
brownie test tests/integration
```

## Deployment

1. If you haven't already, install [Brownie](https://github.com/eth-brownie/brownie):

    ```bash
    pip install eth-brownie
    ```
2. Live deployment

    1. Create the new network folder under [./scripts](scripts) by copying one of the existing ones, the folder name is same as network id added to brownie.(example: brownie --network esc-main, esc-main is the network id)

    2. Modify deploy.py to add `LOCK_TOKEN` address, `NAME` ,  `SYMBOL`, `LOCK_START` ,  `LOCK_END`

    3. Run the deploy.py script:

    ```bash
    brownie run esc-main/deploy deploy --network esc-main
    ```

    4. Once deployment done verify that a `deployment.json` file was created under the network folder, this file contains all contract addresses that have been deployed

    This deploys and links LockedToken contracts.

## License

This project is licensed under the [MIT](LICENSE) license.
