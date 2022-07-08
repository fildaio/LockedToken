import brownie
import pytest

def test_mint_admin_only(alice, bob, locked_token):
    locked_token.mint(alice, 10 ** 18, {"from": alice})

    with brownie.reverts("dev: admin only"):
        locked_token.mint(bob, 10 ** 18, {"from": bob})

def test_total_supply(alice, bob, locked_token):
    locked_token.mint(alice, 10 ** 18, {"from": alice})
    locked_token.mint(bob, 10 ** 18, {"from": alice})

    total_supply = locked_token.totalSupply()
    assert total_supply == 2 * 10 ** 18
