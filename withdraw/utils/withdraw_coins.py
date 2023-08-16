import json
import time
import requests
from web3 import Web3
from withdraw import config
from withdraw.utils.utils import sign_signature, check_fee_balance, deposit_more_funds


def estimate_user_operation(address, cyber_address, amount, chain_id, id_, proxy):
    json_data = {
        'jsonrpc': '2.0',
        'id': id_,
        'method': 'cc_estimateUserOperation',
        'params': [
            {
                'sender': cyber_address,
                'to': address,
                'callData': '0x',
                'value': str(amount),
                'nonce': None,
                'maxFeePerGas': None,
                'maxPriorityFeePerGas': None,
                'ep': '0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789',
            },
            {
                'chainId': chain_id,
                'owner': address,
            },
        ],
    }

    response = requests.post(
        'https://api.cyberconnect.dev/paymaster/',
        headers=config.headers,
        json=json_data,
        proxies=proxy,
    ).json()
    return response['result']['fast'], response['result']['credits']


def get_user_operation(auth, address, cyber_address, token_info, amount, gas, credits_, chain_id, proxy):
    private_headers = config.headers.copy()
    private_headers['authorization'] = auth

    json_data = {
        'query': '\n    mutation sponsorUserOperation($input: SponsorUserOperationInput!) {\n  sponsorUserOperation(input: $input) {\n    userOperation {\n      sender\n      nonce\n      initCode\n      callData\n      callGasLimit\n      verificationGasLimit\n      preVerificationGas\n      maxFeePerGas\n      maxPriorityFeePerGas\n      paymasterAndData\n      signature\n    }\n    userOperationHash\n    errorCode\n  }\n}\n    ',
        'variables': {
            'input': {
                'params': {
                    'sponsorUserOpParams': {
                        'sender': cyber_address,
                        'to': address,
                        'callData': '0x',
                        'value': str(amount),
                        'nonce': None,
                        'maxFeePerGas': gas['maxFeePerGas'],
                        'maxPriorityFeePerGas': gas['maxPriorityFeePerGas'],
                        'entryPoint': '0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789',
                    },
                    'sponsorUserOpContext': {
                        'chainId': chain_id,
                        'owner': address,
                    },
                },
                'type': 'TRANSFER_TOKEN',
                'readableTransaction': f'{{"recipient":"{address}","amount":"{int(amount) / config.coin}","tokenIndex":1,"estimatedFee":{{"value":"{int(credits_) /  config.coin}","tier":"gasPriceFast"}},"token":{{{json.dumps(token_info, separators=(",", ":"))}}}}}',
            },
        },
        'operationName': 'sponsorUserOperation',
    }

    response = requests.post(
        'https://api.cyberconnect.dev/wallet/',
        headers=private_headers,
        json=json_data,
        proxies=proxy,
    ).json()['data']['sponsorUserOperation']

    return response['userOperation'], response['userOperationHash']


def send_user_operation(user_operation, user_address, chain_id, id_):
    json_data = {
        'jsonrpc': '2.0',
        'id': id_,
        'method': 'eth_sendUserOperation',
        'params': [
            user_operation,
            '0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789',
            {
                'chainId': chain_id,
                'owner': user_address,
            },
        ],
    }

    requests.post('https://api.cyberconnect.dev/paymaster/', headers=config.headers, json=json_data).json()


def get_transaction_hash(auth, proxy):
    private_headers = config.headers.copy()
    private_headers['authorization'] = auth

    json_data = {
        'query': '\n    query transactions($after: String) {\n  me {\n    transactions(first: 10, after: $after) {\n      pageInfo {\n        ..._pageInfo\n      }\n      list {\n        txHash\n        chainId\n        name\n        status\n        usdGasFee\n        timestamp\n        credit\n        creditDecimals\n      }\n    }\n  }\n}\n    \n    fragment _pageInfo on PageInfo {\n  hasNextPage\n  hasPreviousPage\n  startCursor\n  endCursor\n}\n    ',
        'variables': {},
        'operationName': 'transactions',
    }

    response = requests.post(
        'https://api.cyberconnect.dev/wallet/',
        headers=private_headers,
        json=json_data,
        proxies=proxy,
    ).json()

    return response["data"]["me"]["transactions"]["list"][0]["txHash"]


def withdraw_coins(user_private: str, user_address: str, cyber_address: str, auth: str, proxies: dict,
                   token_info: dict, web3: Web3):
    chain_id = token_info['chainId']

    if config.amount == 'all' and int(token_info['balance']) > 0:
        amount = token_info['balance']
    elif isinstance(config.amount, float) and int(token_info['balance']) > (config.amount * config.token):
        amount = int(config.amount * config.coin)
    else:
        return False

    last_hash = get_transaction_hash(auth, proxies)
    gas, credits_ = estimate_user_operation(user_address, cyber_address, amount, chain_id, 0, proxies)
    fee_balance = check_fee_balance(auth, proxies)
    if int(credits_) >= fee_balance[0]:
        need2dep = ((int(credits_) - fee_balance[0]) / config.token + 0.1) * 1.8
        deposit_more_funds(web3, cyber_address, need2dep)
        time.sleep(10)

    user_operation, user_operation_hash = get_user_operation(auth, user_address, cyber_address, token_info, amount, gas,
                                                             credits_, chain_id, proxies)
    user_operation['signature'] = sign_signature(user_private, user_operation_hash, web3, type_='hexstr')
    send_user_operation(user_operation, user_address, chain_id, 1)
    if config.wait_tx_hash:
        for i in range(config.max_tx_waiting):
            new_hash = get_transaction_hash(auth, proxies)
            if new_hash != last_hash:
                print(f'\t\tTransaction hash: {new_hash}')
                return new_hash
            if i + 1 == config.max_tx_waiting:
                print(f"\t\tCan't find new hash after {config.max_tx_waiting} retries")
                break
            time.sleep(2)
