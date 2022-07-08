import pytest
from brownie_tokens import ERC20

DAY = 86400
MONTH = 30 * DAY

def approx(a, b, precision=1e-10):
    if a == b == 0:
        return True
    return 2 * abs(a - b) / (a + b) <= precision

@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass

# account aliases


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[2]


# testing contracts


@pytest.fixture(scope="module")
def coin_a():
    yield ERC20("Coin A", "USDA", 18)

@pytest.fixture(scope="module")
def locked_token(coin_a, accounts, chain, LockedToken):
    lock_start = chain[-1].timestamp + DAY
    lock_end = lock_start + MONTH
    token = LockedToken.deploy(coin_a, "LOCKED USDA", "lUSDA", lock_start, lock_end, {"from": accounts[0]})
    yield token

