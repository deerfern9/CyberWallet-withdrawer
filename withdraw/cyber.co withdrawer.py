import requests
from web3 import Web3
from datetime import datetime
from colorama import Fore, init

from utils.utils import read_file, sign_signature, write_to_file
from utils.withdraw_tokens import withdraw_tokens
from utils.withdraw_coins import withdraw_coins
import config
init()

web3 = Web3(Web3.HTTPProvider(config.polygon_rpc))


def get_nonce(address, proxy):
    json_data = {
        'query': '\n    mutation nonce($address: EVMAddress!) {\n  nonce(input: {address: $address}) {\n    status\n    message\n    data\n  }\n}\n    ',
        'variables': {
            'address': address,
        },
        'operationName': 'nonce',
    }

    response = requests.post(
        'https://api.cyberconnect.dev/wallet/',
        headers=config.headers,
        json=json_data,
        proxies=proxy
    ).json()
    nonce = response['data']['nonce']['data']
    return nonce


def get_authorization(address, signature, signed_message, proxy):
    json_data = {
        'query': '\n    mutation login($request: LoginInput!) {\n  login(input: $request) {\n    status\n    message\n    data {\n      accessToken\n      address\n      cyberAccount\n    }\n  }\n}\n    ',
        'variables': {
            'request': {
                'address': address,
                'signature': signature,
                'signedMessage': signed_message,
            },
        },
        'operationName': 'login',
    }

    response = requests.post(
        'https://api.cyberconnect.dev/wallet/',
        headers=config.headers,
        json=json_data,
        proxies=proxy,
    ).json()['data']['login']

    if response['status'] == "SUCCESS":
        authorization = response['data']['accessToken']
        cyber_address = response['data']['cyberAccount']
        return authorization, cyber_address
    else:
        print(f'{response}')


def wallet_balance(address, auth, proxy):
    private_headers = config.headers.copy()
    private_headers['authorization'] = auth
    withdrawal_token, token_chain = config.withdrawal_token_symbol.split('|')
    withdrawal_token_info = None

    json_data = {
        'query': '\n    query tokens {\n  me {\n    tokens {\n      name\n      contract\n      chainId\n      decimals\n      balance\n      symbol\n      cmcTokenId\n      usdPrice\n      cmcUsdPrice\n      priceChange\n    }\n  }\n}\n    ',
        'operationName': 'tokens',
    }

    tokens_balance = requests.post(
        'https://api.cyberconnect.dev/wallet/',
        headers=private_headers,
        json=json_data,
        proxies=proxy,
    ).json()['data']['me']['tokens']

    if tokens_balance:
        print(f"{Fore.MAGENTA}{datetime.now().strftime('%d %H:%M:%S')}{Fore.RESET} | {Fore.CYAN}{address}{Fore.RESET} "
              f"| {Fore.BLUE}CyberWallet balance:")

        for token in tokens_balance:
            symbol = token["symbol"]
            chain_id = token['chainId']
            if symbol.lower() == withdrawal_token.lower() and chain_id == int(token_chain):
                withdrawal_token_info = token
            if token['contract'] == '0x0000000000000000000000000000000000000000':
                print(f'\t\tToken symbol: {symbol} | {chain_id}; Token balance: {int(token["balance"])/config.coin}')
            else:
                print(f'\t\tToken symbol: {symbol} | {chain_id}; Token balance: {int(token["balance"])/config.token}')

        if withdrawal_token == 'all':
            return tokens_balance
        else:
            if not withdrawal_token_info:
                print(f"\t\t{Fore.RED}withdrawal_token_symbol is incorrect or the wallet does not have the required token.{Fore.RESET}")
                return False
            else:
                return [withdrawal_token_info]
    else:
        print(f"{Fore.MAGENTA}{datetime.now().strftime('%d %H:%M:%S')}{Fore.RESET} | {Fore.CYAN}{address}{Fore.RESET} "
              f"| {Fore.RED}CyberWallet balance: {tokens_balance}")

        return False


def main():
    privates = read_file('privates.txt')
    if config.use_proxy:
        proxies = read_file('proxies.txt')

    for private in privates:
        address = web3.eth.account.from_key(private).address

        if config.use_proxy:
            proxy_info = proxies.pop(0)
            proxy = {"http": f"http://{proxy_info}", "https": f"http://{proxy_info}"}
        else:
            proxy = None

        nonce = get_nonce(address, proxy)
        message = f'cyber.co wants you to sign in with your Ethereum account:\n{address}\n\n\nURI: https://cyber.co\nVersion: 1\nChain ID: 56\nNonce: {nonce}\nIssued At: 2023-08-04T10:57:32.803Z\nExpiration Time: 2023-08-18T10:57:32.803Z\nNot Before: 2023-08-04T10:57:32.803Z'
        signed_msg = sign_signature(private, message, web3)
        authorization, cyber_address = get_authorization(address, signed_msg, message, proxy)

        balance = wallet_balance(address, authorization, proxy)
        if bool(balance):
            for token_info in balance:
                print(f'\t\tSending {token_info["symbol"]} to {config.to_address}')
                if token_info['contract'] == '0x0000000000000000000000000000000000000000':
                    tx_hash = withdraw_coins(private, address, cyber_address, authorization, proxy, token_info, web3)
                    if tx_hash:
                        write_to_file('hashes.txt', tx_hash)
                else:
                    tx_hash = withdraw_tokens(private, address, cyber_address, authorization, proxy, token_info, web3)
                    if tx_hash:
                        write_to_file('hashes.txt', tx_hash)


if __name__ == '__main__':
    main()
