import json
import uuid

from web3 import Web3


def create_account():
    acc = Web3().eth.account.create(str(uuid.uuid4()))
    return '{},{}'.format(acc.privateKey.hex(), acc.address)


def batch_create_account(num):
    lines = list()
    for i in range(num):
        lines.append(create_account())

    return lines


def write_file(content, file):
    with open(file, mode='a', encoding='utf8') as f:
        if type(content) == str:
            f.write("\n" + content)
        elif type(content) == dict:
            f.write("\n" + json.dumps(content))
        elif type(content) == list:
            for ln in content:
                f.write(ln)
                if ln.endswith("\n") is False:
                    f.write("\n")
        else:
            raise Exception(f'not support content type: {type(content)}')


if __name__ == '__main__':
    '''
    批量生成账号，格式：
    私钥,地址
    '''

    print('请输入生成账号的数量：')
    n = input('')
    accounts = batch_create_account(int(n))
    write_file(accounts, './batch_acc.txt')
