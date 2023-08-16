# # # # # # # Chains ID # # # # # # # # #
#                                       #
#            polygin = 137              #
#            optimism = 10              #
#            base = 137                 #
#            linea = 137                #
#                                       #
# # # # # # # # # # # # # # # # # # # # #

withdrawal_token_symbol = 'cyber|10'                                   # token_symbol|chainId or all|chainId
amount = 'all'                                                         # all(string)/custom(float)
sponsor_private = ''                                                   # main private with matic
to_address = ''                                                        # withdrawal recipient address
use_proxy = False                                                      # True - using proxy from proxies.txt, False - don't
wait_tx_hash = True                                                    # True - waiting transaction hash from CyberWallet, False - don't
max_tx_waiting = 10                                                    # max retries for searching transaction hash

polygon_rpc = "https://polygon.blockpi.network/v1/rpc/7433894eead0d1c58dbc40da4635dd42fd6cd8cb"

cyber_contract_address = '0xcd97405Fb58e94954E825E46dB192b916A45d412'
cyber_contract_abi = '[{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"from","type":"address"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdraw","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"depositTo","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"deposits","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

headers = {
    'authority': 'api.cyberconnect.dev',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,ru;q=0.5,en-US;q=0.4',
    'authorization': '',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://wallet.cyber.co',
    'pragma': 'no-cache',
    'referer': 'https://wallet.cyber.co/',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

coin = 1_000_000_000_000_000_000                                          # the number of zeros in one coin  | 10^18
token = 1_000_000                                                         # the number of zeros in one token | 10^6
