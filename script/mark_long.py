import hashlib
import json
import random
import time
from datetime import datetime, timedelta

import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware

# **************************************** CONSTANT *****************************************************
# The maximum acceptable base fee.
GAS_LIMIT = random.randint(877000, 877500)

rpc_url = "https://rpc.test.deriw.com/"
EXPLORER_HOST = "https://explorer.test.deriw.com"
Chain_id = 35318034165
DEX_CONTRACT_ADDRESS = "0x9Fb76a6B771B39B1BC138C1e7b4a7a4E2a53cCD4"
ERC20_CONTRACT_ADDRESS = "0x2861644dC8723b30D10EEd2474F5c7d6D5F386FD"
SPENDER_ADDRESS = '0xc341cCD15cb8dC4e1020FC06EeF53aCb6010DDE1'

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

E_18 = 1000000000000000000
E_12 = 1000000000000

DEX_ABI = [
    {
        "inputs": [],
        "name": "claim",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address[]",
                "name": "erc20",
                "type": "address[]"
            },
            {
                "internalType": "address",
                "name": "noknown",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "payAmount",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "p2",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "p3",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "p4",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "p5",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "p6",
                "type": "uint256"
            }
        ],
        "name": "createDecreasePosition",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

ERC20_CONTRACT_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }, {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
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
def balanceOf(account):
    contract_instance = w3.eth.contract(address=ERC20_CONTRACT_ADDRESS, abi=ERC20_CONTRACT_ABI)
    return contract_instance.functions.balanceOf(account).call()


def allowance(owner, spender):
    contract_instance = w3.eth.contract(address=ERC20_CONTRACT_ADDRESS, abi=ERC20_CONTRACT_ABI)
    return contract_instance.functions.allowance(owner, spender).call()


def approve(private_key, erc20_address, spender, amount):
    contract_instance = w3.eth.contract(address=ERC20_CONTRACT_ADDRESS, abi=ERC20_CONTRACT_ABI)
    tx = contract_instance.functions.approve(spender, amount).buildTransaction(
        {
            "chainId": Chain_id,
            'from': from_key(private_key),
            'nonce': w3.eth.getTransactionCount(from_key(private_key)),
            'gas': 60981,
            "maxFeePerGas": Web3.toWei(0, 'wei'),
            "maxPriorityFeePerGas": Web3.toWei(0, 'wei'),
        }
    )
    return send_transaction(tx, private_key, erc20_address)


def get_amount_from_erc20(wallet_address):
    contract_instance = w3.eth.contract(address=ERC20_CONTRACT_ADDRESS, abi=ERC20_CONTRACT_ABI)
    return contract_instance.functions.balanceOf(wallet_address).call()


def generate_claim_transaction_dict(account_from, param):
    contract_instance = w3.eth.contract(address=DEX_CONTRACT_ADDRESS, abi=DEX_ABI)

    usdt_amount = param[0]
    p1 = param[1]
    p2 = param[2]
    tx = contract_instance.functions.createDecreasePosition([ERC20_CONTRACT_ADDRESS],
                                                            '0xb86b491dA10f9194C0C5c0B29cD1298fAf1A634A',
                                                            usdt_amount, p1, 1, p2, 0, 0).buildTransaction(
        {
            "chainId": Chain_id,
            'from': account_from,
            'nonce': w3.eth.getTransactionCount(account_from),
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
    print("[{}]===> account:{} tx hash:{} ".format(get_current_time(), address, tx_hash.hex()))
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("[{}]===>  address={} has complete the transaction: {}/tx/{}!".format(get_current_time(), address,
                                                                                EXPLORER_HOST, tx_hash.hex()))
    return tx_hash.hex()


def read_line(file):
    arr = list()
    with open(file, mode='r', encoding='utf8') as f:
        for ln in f:
            arr.append(ln.replace("\n", ""))
    return arr


# **************************************** Claim functions ****************************************************


def do_long(private_key, param):
    wallet_address = from_key(private_key)
    tx_dict = generate_claim_transaction_dict(wallet_address, param)
    tx_dict['data'] = '0x2e24d502' + tx_dict['data'][10:]
    tx_hash = send_transaction(tx_dict, private_key, wallet_address)
    print("[{}]===> market long success")
    return tx_hash


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def from_key(privateKey):
    acc = Web3().eth.account.from_key(privateKey)
    return acc.address


def get_five_minute_ago():
    now = datetime.now()
    get_five_minute_ago = now - timedelta(minutes=5)
    return int(get_five_minute_ago.timestamp())


def get_time():
    # 获取当前时间
    now = datetime.now()

    # 获取当前时间的分钟数
    current_minute = now.minute

    # 计算距离下一个5分钟间隔还有多少分钟
    minutes_to_next_interval = (current_minute % 5)

    # 如果当前分钟已经是5的倍数，‌那么minutes_to_next_interval将为0，‌我们不需要调整
    if minutes_to_next_interval == 0:
        next_time = now
    else:
        # 计算下一个5分钟的时间点
        next_time = now - timedelta(minutes=minutes_to_next_interval)
    return int(next_time.timestamp() / 100) * 100


def get_eth_price():
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://deriw.com',
        'Referer': 'https://deriw.com/',
        'User-Agent': USER_AGENT
    }
    j = json.loads("{\"data\":{\"prices\":null}}")
    while 'prices' not in j['data'] or j['data']['prices'] is None:
        url = 'https://api.test.deriw.com/client/candles?symbol=WETH&preferable_chain_id=97&period=5m&from=' + str(
            get_five_minute_ago()) + '&limit=1'
        res = requests.get(url, headers=headers)
        j = json.loads(res.text)
        if j['data']['prices'] is None:
            print("wating eth price...")
            time.sleep(5)
    return float(j['data']['prices'][0]['c'])


def build_param(u, lever):
    eth_price = get_eth_price()
    eth_price = eth_price + 2.62
    eth_price = int(eth_price * E_12) * E_18
    leverage_amount = u * lever * E_18 * E_12
    leverage_amount = leverage_amount - random.randint(100000, 474400000000000)
    return u * E_18, leverage_amount, eth_price


def check_and_approve(pk):
    allowance_amount = allowance(from_key(pk), SPENDER_ADDRESS)
    if balanceOf(from_key(pk)) > allowance_amount:
        print("[{}]===> send approve tx:{}".format(get_current_time(), ERC20_CONTRACT_ADDRESS))
        tx_hash = approve(pk, ERC20_CONTRACT_ADDRESS, SPENDER_ADDRESS, 1000000000 * E_18)
        print("[{}]===> send approve tx:{} success".format(tx_hash))


def calculate_md5(data):
    # 创建一个 md5 对象
    md5_hash = hashlib.md5()

    # 更新 md5 对象的内容
    md5_hash.update(data.encode('utf-8'))

    # 获取计算得到的 MD5 值
    md5_value = md5_hash.hexdigest()

    return md5_value


def create_log(account):
    url = 'https://api.test.deriw.com/risk_control/user_info/create_log'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://deriw.com',
        'Referer': 'https://deriw.com/',
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,
    }
    device = calculate_md5(account)
    device = "{}-{}-{}-{}-{}".format(device[0:8], device[8:12], device[12:16], device[16:20], device[20:])
    ip = "1.65.218.81"
    data = {"address": account, "type": 1, "ip": ip, "device": device, "client": "web"}

    res = requests.post(url, headers=headers, data=json.dumps(data))
    assert 200 == json.loads(res.text)['status']


def batch_market(usdt, leverage):
    print("[{}]=====> 开始发送交易，支付金额：{} USDT, 杠杆倍数：{}".format(get_current_time(), usdt, leverage))
    excel_path = 'pk.txt'
    rows = read_line(excel_path)
    print("[{}]=====> 开杠杆的账户数量：{}".format(get_current_time(), len(rows)))
    print("[{}]=====> 确认开始发送交易？ Y/N".format(get_current_time()))
    if 'Y' == input('').upper():
        for pk in rows:
            pk = pk.split(',')[0]
            check_and_approve(pk)
            p = build_param(usdt, leverage)

            # create_log(from_key(pk))
            tx_hash = do_long(pk, p)
            print("{}/tx/{}".format(EXPLORER_HOST, tx_hash))
            time.sleep(random.randint(2, 6))


def input_param():
    print('请输入下单金额(USDT)：')
    try:
        usdt = int(input(''))
    except ValueError:
        print("金额应为数字！！")
        exit(1)
    print('请输入杠杆倍数：')
    try:
        leverage = int(input(''))
        if leverage < 2 or leverage > 100:
            raise ValueError
    except ValueError:
        print("杠杆应为2~100的数字！！")
        exit(1)
    return usdt, leverage


if __name__ == '__main__':
    '''
    在同级目录创建文件：pk.txt
    市价做多。
    '''
    in_param = input_param()
    batch_market(in_param[0], in_param[1])