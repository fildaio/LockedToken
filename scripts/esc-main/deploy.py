
from .. import deploy_token

from brownie import network

DEPLOYMENTS_JSON = "scripts/" + network.main.show_active() + "/deployments.json"

LOCK_TOKEN = "0x00E71352c91Ff5B820ab4dF08bb47653Db4e32C0"
NAME = "TEST_LOCK_FILDA"
SYMBOL = "tlockFilDA"
LOCK_START = 1658736065
LOCK_END = LOCK_START + 365 * 86400

def deploy():
    admin = deploy_token.get_live_admin()
    deploy_token.development(admin, LOCK_TOKEN, NAME, SYMBOL, LOCK_START, LOCK_END, deploy_token.REQUIRED_CONFIRMATIONS, DEPLOYMENTS_JSON)
