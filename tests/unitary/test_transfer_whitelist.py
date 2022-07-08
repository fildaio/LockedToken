import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, locked_token):
    locked_token.mint(alice, 2 * 10 ** 18, {"from": alice})
    locked_token.mint(bob, 10 ** 18, {"from": alice})


def test_set_whitelist_admin_only(alice, bob, locked_token):
    locked_token.set_transfer_whitelist(alice, True, {"from": alice})

    with brownie.reverts("dev: admin only"):
        locked_token.set_transfer_whitelist(bob, True, {"from": bob})

def test_read_whitelist(alice, locked_token):
    isInWhitelist = locked_token.is_in_whitelist(alice)
    assert isInWhitelist == False

    locked_token.set_transfer_whitelist(alice, True, {"from": alice})
    isInWhitelist = locked_token.is_in_whitelist(alice)
    assert isInWhitelist == True


def test_whitelist_transfer_only(alice, bob, locked_token):
    locked_token.set_transfer_whitelist(alice, True, {"from": alice})
    locked_token.transfer(bob, 10 ** 18, {"from": alice})

    assert locked_token.balanceOf(alice) == 10 ** 18
    assert locked_token.balanceOf(bob) == 2 * 10 ** 18

    locked_token.set_transfer_whitelist(alice, False, {"from": alice})
    with brownie.reverts("dev: transfer whitelist only"):
        locked_token.transfer(bob, 10 ** 18, {"from": alice})

    with brownie.reverts("dev: transfer whitelist only"):
        locked_token.transfer(alice, 10 ** 18, {"from": bob})

