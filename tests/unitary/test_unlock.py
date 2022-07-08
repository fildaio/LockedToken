import math
import brownie
import pytest

from tests.conftest import approx

DAY = 86400
WEEK = 7 * DAY
MONTH = 30 * DAY
MULTIPLIER = 10 ** 18

@pytest.fixture(scope="module", autouse=True)
def setup(alice, locked_token):
    locked_token.mint(alice, 10 ** 21, {"from": alice})
    locked_token.set_transfer_whitelist(alice, True, {"from": alice})

def test_unlock_amount(alice, locked_token, chain):
    unlock_amount = locked_token.unlock_amount(alice)
    assert unlock_amount == 0

    # at the lock start time, the unlock amount is 0
    chain.sleep(DAY)
    chain.mine()

    unlock_amount = locked_token.unlock_amount_write.call(alice)
    assert unlock_amount == 0

    # after the lock start time, the unlock amount is bigger than 0
    chain.sleep(DAY)
    chain.mine()

    unlock_amount = locked_token.unlock_amount_write.call(alice)
    assert unlock_amount > 0

    # after lock end time, the unlock amount is balance of user
    chain.sleep(MONTH)
    chain.mine()

    unlock_amount = locked_token.unlock_amount_write.call(alice)
    assert unlock_amount == locked_token.balanceOf(alice)

def test_unlock_amount_detail(alice, locked_token, chain):
    # at the lock start time, the unlock amount is 0
    chain.sleep(DAY)
    chain.mine()

    chain.sleep(WEEK)
    chain.mine()

    (slope, bias, ts) = locked_token.user_point(alice)
    expect = 10 ** 21 * MULTIPLIER // MONTH
    assert slope == expect

    locked_token.checkpoint(alice)

    expect = 10 ** 21 * MULTIPLIER // MONTH * WEEK // MULTIPLIER
    unlock_amount = locked_token.unlock_amount(alice)

    assert approx(unlock_amount, expect, 1.001 / WEEK)

def test_unlock(alice, locked_token, chain, coin_a):
    chain.sleep(WEEK)
    chain.mine()

    (slope_old, bias, ts) = locked_token.user_point(alice)
    total_supply_before = locked_token.totalSupply()

    coin_a._mint_for_testing(locked_token.address, 10 ** 21)
    unlock_amount = locked_token.unlock_amount_write.call(alice)
    locked_token.unlock(alice)

    (slope_new, bias, ts) = locked_token.user_point(alice)
    balance = coin_a.balanceOf(alice)
    total_supply_after = locked_token.totalSupply()

    assert approx(unlock_amount, balance, 1.001 / WEEK)
    assert unlock_amount == locked_token.user_unlocked(alice)
    assert slope_old == slope_new
    assert locked_token.unlock_amount(alice) == 0
    assert total_supply_after == total_supply_before - balance

def test_unlock_amount_add(alice, bob, locked_token, chain):
    # sleep to start time
    chain.sleep(DAY)
    chain.mine()

    locked_token.mint(bob, 10 ** 21, {"from": alice})
    bob_unlock = locked_token.unlock_amount(bob)
    assert bob_unlock == 0

    chain.sleep(WEEK)
    chain.mine()

    (slope_old, bias, ts) = locked_token.user_point(alice)
    locked_token.mint(alice, 10 ** 21, {"from": alice})
    (slope, bias, ts) = locked_token.user_point(alice)
    expect = 10 ** 21 * MULTIPLIER // MONTH + 10 ** 21 * MULTIPLIER // (23 * DAY)

    assert slope == expect
    #assert approx(slope, expect, 1e-06)
    assert bias == slope_old * WEEK // MULTIPLIER

    locked_token.checkpoint(alice)
    assert locked_token.unlock_amount(alice) == bias

def test_unlock_amount_cross_lock_end(alice, locked_token, chain):
    chain.sleep(WEEK)
    chain.mine()

    locked_token.mint(alice, 10 ** 21, {"from": alice})
    (slope_old, bias, ts) = locked_token.user_point(alice)

    chain.sleep(MONTH)
    chain.mine()

    locked_token.mint(alice, 10 ** 21, {"from": alice})
    (slope_new, bias, ts) = locked_token.user_point(alice)
    assert slope_old == slope_new
    assert locked_token.unlock_amount(alice) == locked_token.balanceOf(alice)

def test_unlock_multiple_user(alice, bob, charlie, locked_token, chain, coin_a):
    chain.sleep(DAY)
    chain.mine()

    # mint lock token to LockedToken contract, alice/bob/charlie 's balance
    coin_a._mint_for_testing(locked_token.address, 10 ** 21)
    coin_a._mint_for_testing(locked_token.address, 10 ** 21)
    coin_a._mint_for_testing(locked_token.address, 10 ** 21)

    chain.sleep(WEEK)
    chain.mine()

    locked_token.mint(bob, 10 ** 21, {"from": alice})
    assert locked_token.unlock_amount(bob) == 0

    alice_unlock = locked_token.unlock_amount_write.call(alice)
    locked_token.unlock(alice)
    alice_balance = coin_a.balanceOf(alice)
    assert approx(alice_unlock, alice_balance, 1.001 / WEEK)

    chain.sleep(WEEK)
    chain.mine()

    locked_token.mint(charlie, 10 ** 21, {"from": alice})
    assert locked_token.unlock_amount(charlie) == 0

    bob_unlock = locked_token.unlock_amount_write.call(bob)
    locked_token.unlock(bob)
    bob_balance = coin_a.balanceOf(bob)
    assert approx(bob_unlock, bob_balance, 1.001 / WEEK)

    chain.sleep(WEEK)
    chain.mine()

    charlie_unlock = locked_token.unlock_amount_write.call(charlie)
    locked_token.unlock(charlie)
    charlie_balance = coin_a.balanceOf(charlie)
    assert approx(charlie_unlock, charlie_balance, 1.001 / WEEK)
