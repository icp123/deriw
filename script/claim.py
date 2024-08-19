import random
import time

from web3 import Web3
from web3.middleware import geth_poa_middleware

# **************************************** CONSTANT *****************************************************
# The maximum acceptable base fee.
GWEI = 1000000000
GAS_LIMIT = 200000

rpc_url = "https://rpc.test.deriw.com/"
EXPLORER_HOST = "https://explorer.test.deriw.com"
Chain_id = 35318034165
AIRDROP_CONTRACT_ADDRESS = "0x1206f4f4dE5F7B06563880a50B866bB29247AD2e"
ERC20_CONTRACT_ADDRESS = "0x2861644dC8723b30D10EEd2474F5c7d6D5F386FD"

AIRDROP_ABI = [{"inputs": [], "name": "claim", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]

ERC20_CONTRACT_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint8",
                        "name": "_v",
                        "type": "uint8"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "_r",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "_s",
                        "type": "bytes32"
                    }
                ],
                "internalType": "struct RelationMedal.Signature",
                "name": "signature",
                "type": "tuple"
            },
            {
                "internalType": "uint256",
                "name": "expireTime",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_pIndex",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_oIndex",
                "type": "uint256"
            }
        ],
        "name": "claim",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

w3 = Web3(Web3.HTTPProvider(rpc_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


# **************************************** Base function of contract ***********************************************

def get_amount_from_erc20(wallet_address):
    contract_instance = w3.eth.contract(address=ERC20_CONTRACT_ADDRESS, abi=ERC20_CONTRACT_ABI)
    return contract_instance.functions.balanceOf(wallet_address).call()


def generate_claim_transaction_dict(account_from):
    contract_instance = w3.eth.contract(address=AIRDROP_CONTRACT_ADDRESS, abi=AIRDROP_ABI)
    print("[{}]=====> maxFeePerGas:{} GWEI,priority:{} GEI".format(get_current_time(), 0 / GWEI, 0 / GWEI))

    tx = contract_instance.functions.claim().buildTransaction(
        {
            "chainId": Chain_id,
            'from': account_from,
            'nonce': w3.eth.getTransactionCount(account_from),
            # gas limit
            'gas': GAS_LIMIT,
            "maxFeePerGas": Web3.toWei(0, 'wei'),
            "maxPriorityFeePerGas": Web3.toWei(0, 'wei'),
        }
    )
    return tx


def send_transaction(transaction_dict, private_key, address):
    print("[{}]===> start send_tx address:{}  ".format(get_current_time(), address))

    tx_create = w3.eth.account.signTransaction(transaction_dict, private_key)
    tx_hash = w3.eth.sendRawTransaction(tx_create.rawTransaction)
    print("[{}]===> privateKey:{} tx hash:{} ".format(get_current_time(), private_key, tx_hash.hex()))
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("[{}]===>  address={} has complete the transaction!".format(get_current_time(), address))
    return tx_hash.hex()


def read_line(file):
    arr = list()
    with open(file, mode='r', encoding='utf8') as f:
        for ln in f:
            arr.append(ln.replace("\n", ""))
    return arr


# **************************************** Claim functions ****************************************************


def claim(private_key):
    wallet_address = from_key(private_key)
    tx_dict = generate_claim_transaction_dict(wallet_address)
    return send_transaction(tx_dict, private_key, wallet_address)


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def from_key(privateKey):
    acc = Web3().eth.account.from_key(privateKey)
    return acc.address


def batch_claim():
    excel_path = 'pk.txt'
    rows = read_line(excel_path)
    for r in rows:
        balance = get_amount_from_erc20(from_key(r.split(',')[0]))
        print(balance)
        tx_hash = claim(r.split(',')[0])
        print("{}/tx/{}".format(EXPLORER_HOST, tx_hash))
        time.sleep(random.uniform(1, 5))


if __name__ == '__main__':
    '''
    在同级目录创建文件：pk.txt
    '''
    batch_claim()
