from eth_account.messages import encode_defunct
import requests

from withdraw import config


def read_file(filename):
    result = []
    with open(filename, 'r') as file:
        for tmp in file.readlines():
            result.append(tmp.replace('\n', ''))

    return result


def write_to_file(filename, text):
    with open(filename, 'a') as file:
        file.write(f'{text}\n')


def sign_signature(private_key, message, web3, type_='text'):
    if type_ == 'hexstr':
        message_hash = encode_defunct(hexstr=message)
    else:
        message_hash = encode_defunct(text=message)
    signed_message = web3.eth.account.sign_message(message_hash, private_key)

    signature = signed_message.signature.hex()
    return signature


def check_fee_balance(authorization, proxy):
    private_headers = config.headers.copy()
    private_headers['authorization'] = authorization

    json_data = {
        'query': '\n    query creditInfo {\n  me {\n    credits {\n      balance\n      pending\n      decimals\n      locked\n      contract\n    }\n  }\n}\n    ',
        'operationName': 'creditInfo',
    }

    fee_balance = int(requests.post(
        'https://api.cyberconnect.dev/wallet/',
        headers=private_headers,
        json=json_data,
        proxies=proxy
    ).json()['data']['me']['credits'][0]['balance'])

    return fee_balance, fee_balance / config.token


def deposit_more_funds(web3, cyber_address, amount):
    sponsor_address = web3.eth.account.from_key(config.sponsor_private).address
    cyber_contract = web3.eth.contract(address=web3.to_checksum_address(config.cyber_contract_address),
                                       abi=config.cyber_contract_abi)

    try:
        tx = cyber_contract.functions.depositTo(cyber_address).build_transaction(
            {
                'from': sponsor_address,
                'value': web3.to_wei(amount, 'ether'),
                'nonce': web3.eth.get_transaction_count(sponsor_address),
                'gasPrice': web3.eth.gas_price,
            }
        )

        tx_create = web3.eth.account.sign_transaction(tx, config.sponsor_private)
        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)
        write_to_file('hashes.txt', tx_hash.hex())
        print(f"{sponsor_address} | Depositing hash: {tx_hash.hex()}")
        web3.eth.wait_for_transaction_receipt(tx_hash, timeout=360)
    except Exception as e:
        print(f'{sponsor_address} | ERROR: {e}')