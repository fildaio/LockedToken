import json

from brownie import (
    LockedToken,
    web3,
    accounts,
    history,
    ZERO_ADDRESS
)

REQUIRED_CONFIRMATIONS = 3

def get_live_admin():
    # Admin and funding admin account objects used for in a live environment
    # May be created via accounts.load(name) or accounts.add(privkey)
    # https://eth-debrownie.readthedocs.io/en/stable/account-management.html
    admin = accounts.load("test1")
    return admin


def development(admin, token, name, symbol, lock_start, lock_end, confs=1, deployments_json=None):
    lockedToken = LockedToken.deploy(
        token,
        name,
        symbol,
        lock_start,
        lock_end,
        {"from": admin, "required_confs": confs},
    )
    deployments = {
        "LockedToken": lockedToken.address,
    }
    if deployments_json is not None:
        with open(deployments_json, "w") as fp:
            json.dump(deployments, fp)
        print(f"Deployment addresses saved to {deployments_json}")
