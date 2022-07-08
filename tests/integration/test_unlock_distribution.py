
import brownie
from brownie import ZERO_ADDRESS, chain
from brownie.test import strategy

from tests.conftest import approx


class StateMachine:
    """
    Validate that eventually users claim almost all rewards (except for dust)
    """

    st_account = strategy("address", length=5)
    st_value = strategy("uint64", min_value=10 ** 10)
    st_time = strategy("uint", max_value=7 * 86400)

    def __init__(self, accounts, coin_a, locked_token):
        self.accounts = accounts
        self.token = locked_token
        self.coin = coin_a

    def setup(self):
        self.balances = {i: 0 for i in self.accounts}
        self.unlockBalances = {i: 0 for i in self.accounts}
        self.total_balances = 0

    def rule_mint(self, st_account, st_value):
        """
        Mint new locked token to user.

        Because of the upper bound of `st_value` relative to the initial account
        balances, this rule should never fail.
        """

        self.coin._mint_for_testing(self.token.address, st_value)
        self.token.mint(st_account, st_value, {"from": self.accounts[0]})

        self.balances[st_account] += st_value
        self.total_balances += st_value

    def rule_unlock(self, st_account):
        balance_old = self.coin.balanceOf(st_account)
        self.token.unlock(st_account)
        balance_new = self.coin.balanceOf(st_account)
        unlock = balance_new - balance_old

        if unlock > 0:
            self.balances[st_account] -= unlock
            self.total_balances -= unlock
            self.unlockBalances[st_account] += unlock

        assert self.unlockBalances[st_account] == self.token.user_unlocked(st_account)

    def rule_advance_time(self, st_time):
        """
        Advance the clock.
        """
        chain.sleep(st_time)

    def rule_checkpoint(self, st_account):
        """
        Create a new user checkpoint.
        """
        self.token.checkpoint(st_account)

    def invariant_balances(self):
        """
        Validate expected balances against actual balances.
        """
        for account, balance in self.balances.items():
            assert self.token.balanceOf(account) == balance

    def invariant_total_supply(self):
        """
        Validate expected total supply against actual total supply.
        """
        assert self.token.totalSupply() == sum(self.balances.values())

    def teardown(self):
        """
        The unlocked amount is equal to the total sub balance of LockedToken contract
        """

        coin_supply = self.coin.totalSupply()

        assert coin_supply - self.coin.balanceOf(self.token.address) == sum(self.unlockBalances.values())

def test_state_machine(
    state_machine, accounts, coin_a, locked_token
):

    chain.sleep(86400)

    # because this is a simple state machine, we use more steps than normal
    settings = {"stateful_step_count": 25, "max_examples": 30}

    state_machine(
        StateMachine,
        accounts[:5],
        coin_a,
        locked_token,
        settings=settings,
    )
