# @version 0.2.12
"""
@title Locked Token
@author FilDA Finance
@license MIT
@notice The token is locked, unlock depending on time
"""

interface ERC20:
    def decimals() -> uint256: view
    def name() -> String[64]: view
    def symbol() -> String[32]: view
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(spender: address, to: address, amount: uint256) -> bool: nonpayable

struct Point:
    slope: uint256  #  dweight / dt
    bias: uint256
    ts: uint256

event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _value: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address

event TransferWhitelistChanged:
     _addr: indexed(address)
     _allow: bool

event Unlocked:
     _addr: indexed(address)
     _amount: uint256

event SetMinter:
    minter: address

MULTIPLIER: constant(uint256) = 10 ** 18

name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)

balanceOf: public(HashMap[address, uint256])
allowances: HashMap[address, HashMap[address, uint256]]
total_supply: uint256

lock_token: public(address)

lock_start: public(uint256)
lock_end: public(uint256)

user_point: public(HashMap[address, Point])  # user -> Point
user_unlocked: public(HashMap[address, uint256]) # user -> unlocked amount

transfer_whitelist: HashMap[address, bool] # only in whitelist is allowed to transfer

admin: public(address)
future_admin: public(address)


@external
def __init__(token_addr: address, _name: String[64], _symbol: String[32], _lock_start: uint256, _lock_end: uint256):
    """
    @notice Contract constructor
    @param token_addr dao token address
    @param _name Token name
    @param _symbol Token symbol
    """
    self.admin = msg.sender
    self.lock_token = token_addr
    self.name = _name
    self.symbol = _symbol

    assert (_lock_end > _lock_start) and (_lock_start > block.timestamp)
    self.lock_start = _lock_start
    self.lock_end = _lock_end

    _decimals: uint256 = ERC20(token_addr).decimals()
    assert _decimals <= 255
    self.decimals = _decimals

@internal
def _checkpoint(_addr: address, _value: uint256):
    """
    @notice Only update user point after value added
    """

    point: Point = self.user_point[_addr]
    if point.ts == 0:
        point.ts = block.timestamp
    if point.ts >= self.lock_end:
        return

    assert(point.ts <= block.timestamp)
    new_point: Point = point

    lock_start: uint256 = self.lock_start
    lock_end: uint256 = self.lock_end

    if _value > 0:
        dt: uint256 = 0
        if block.timestamp <= lock_start:
            dt = lock_end - lock_start
        elif block.timestamp <= lock_end:
            dt = lock_end - block.timestamp

        if dt > 0:
          new_point.slope += _value * MULTIPLIER / dt

    if block.timestamp > lock_start:
        dt: uint256 = 0
        if point.ts < lock_start:
            dt = block.timestamp - lock_start
        elif block.timestamp <= lock_end:
            dt = block.timestamp - point.ts
        else:
            dt = lock_end - point.ts

        new_point.bias += point.slope * dt / MULTIPLIER

    new_point.ts = block.timestamp
    self.user_point[_addr] = new_point

@external
def checkpoint(_addr: address):
    self._checkpoint(_addr, 0)

@internal
@view
def _unlock_amount(_addr: address) -> uint256:
    if block.timestamp <= self.lock_start:
        return 0

    user_balance: uint256 = self.balanceOf[_addr]
    if block.timestamp >= self.lock_end:
        return user_balance

    point: Point = self.user_point[_addr]
    unlock_amount: uint256 = point.bias - self.user_unlocked[_addr]

    return unlock_amount

@external
@view
def unlock_amount(_addr: address) -> uint256:
    """
    @notice Get the number of unlock for a user
    @dev This call does not consider pending amount from last checkpoint.
         Off-chain callers should instead use `unlock_amount_write` as a
         view method.
    @param _addr Account to get unlock amount for
    @return uint256 Unlock token amount
    """
    _value: uint256 = self._unlock_amount(_addr)
    _balance: uint256 = self.balanceOf[_addr]
    if _value > _balance:
        _value = _balance
    return _value

@external
def unlock_amount_write(_addr: address) -> uint256:
    """
    @notice Get the number of unlock for a user
    @dev This function should be manually changed to "view" in the ABI
    @param _addr Account to get unlock amount for
    @return uint256 Unlock token amount
    """

    # update user's unlock amount
    self._checkpoint(_addr, 0)

    _value: uint256 = self._unlock_amount(_addr)
    _balance: uint256 = self.balanceOf[_addr]
    if _value > _balance:
        _value = _balance
    return _value

@external
def commit_transfer_ownership(addr: address):
    """
    @notice Transfer ownership of VotingEscrow contract to `addr`
    @param addr Address to have ownership transferred to
    """
    assert msg.sender == self.admin  # dev: admin only
    self.future_admin = addr
    log CommitOwnership(addr)


@external
def apply_transfer_ownership():
    """
    @notice Apply ownership transfer
    """
    assert msg.sender == self.future_admin  # dev: future admin only
    _admin: address = self.future_admin
    assert _admin != ZERO_ADDRESS  # dev: admin not set
    self.admin = _admin
    self.future_admin = ZERO_ADDRESS
    log ApplyOwnership(_admin)

@external
def mint(_to: address, _value: uint256) -> bool:
    """
    @notice Mint `_value` tokens and assign them to `_to`
    @dev Emits a Transfer event originating from 0x00
    @param _to The account that will receive the created tokens
    @param _value The amount that will be created
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin only
    assert _to != ZERO_ADDRESS  # dev: zero address

    _total_supply: uint256 = self.total_supply + _value
    self.total_supply = _total_supply

    self.balanceOf[_to] += _value
    self._checkpoint(_to, _value)
    log Transfer(ZERO_ADDRESS, _to, _value)

    return True


@internal
def _burn(_addr: address, _value: uint256) -> bool:
    """
    @notice Burn `_value` tokens belonging to `msg.sender`
    @dev Emits a Transfer event with a destination of 0x00
    @param _value The amount that will be burned
    @return bool success
    """
    self.balanceOf[_addr] -= _value
    self.total_supply -= _value

    log Transfer(_addr, ZERO_ADDRESS, _value)
    return True

@external
@view
def totalSupply() -> uint256:
    """
    @notice Total number of tokens in existence.
    """
    return self.total_supply

@external
@view
def is_in_whitelist(_addr: address) -> bool:
    """
    @return bool is allowed to transfer
    """
    return self.transfer_whitelist[_addr]

@external
def transfer(_to : address, _value : uint256) -> bool:
    """
    @notice Transfer `_value` tokens from `msg.sender` to `_to`
    @dev Vyper does not allow underflows, so the subtraction in
         this function will revert on an insufficient balance
    @param _to The address to transfer to
    @param _value The amount to be transferred
    @return bool success
    """
    assert self.transfer_whitelist[msg.sender] # dev: transfer whitelist only
    assert _to != ZERO_ADDRESS  # dev: transfers to 0x0 are not allowed
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    self._checkpoint(_to, _value)
    log Transfer(msg.sender, _to, _value)
    return True

@external
def set_transfer_whitelist(_addr: address, _allow: bool):
    """
    @notice allow the ‘_addr’ transfer or not
    @param _addr The address set in transfer whitelist
    @param _allow True means allow the _addr transfer token
    """

    assert msg.sender == self.admin  # dev: admin only
    self.transfer_whitelist[_addr] = _allow

    log TransferWhitelistChanged(_addr, _allow)

@external
@nonreentrant('lock')
def unlock(_addr: address = msg.sender) -> uint256:
    """
    @notice Unlock the locked token
    @param _addr The address to unlock
    """

    # update user's unlock amount
    self._checkpoint(_addr, 0)

    unlock_amount: uint256 = self._unlock_amount(_addr)
    unlocked: uint256 = self.user_unlocked[_addr]

    assert unlock_amount <= self.balanceOf[_addr] # dev: unlock amount is bigger than balance

    if unlock_amount > 0:
        unlocked += unlock_amount
        self.user_unlocked[_addr] = unlocked

        self._burn(_addr, unlock_amount)
        ERC20(self.lock_token).transfer(_addr, unlock_amount)

        log Unlocked(_addr, unlock_amount)

    return unlock_amount


