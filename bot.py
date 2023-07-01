import time
import datetime
from brownie import *
import json
import os

# follow these instructions to get API key
# https://docs.snowtrace.io/getting-started/viewing-api-usage-statistics
os.environ['SNOWTRACE_TOKEN'] = 'API_KEY_HERE'

# connect to network first                                                                                              
if network.is_connected():
    network.disconnect()
    pass

# connect to avax  c-chain                                                                                              
network.connect('avax-main')

# load wallet. you will need to create and load your own
user = accounts.load('WALLET_NAME', password='PASSWORD')

# this keeps track of when contracts were last loaded                                                                       
loadContractTime = 0

while True:
    if time.time() - loadContractTime > 120:
        # every 60s refresh contract from snowtrace                                                                     
        loadContractTime = time.time()

        dai = Contract.from_explorer('0xd586e7f844cea2f87f50152665bcbc2c279d8d70')
        usdc = Contract.from_explorer('0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e')
        wavax = Contract.from_explorer('0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7')
        router = Contract.from_explorer('0x60aE616a2155Ee3d9A68541Ba4544862310933d4')

    pairs = [(dai, usdc), (usdc, dai)]

    for (a,b) in pairs:
        # For max amount change to amountIn to:                                                                         
        # amountIn = a.balanceOf(user.address)                                                                          

        # Only execute single dollar trades                                                                             
        amountIn = 1*10**a.decimals()
        amountOut = router.getAmountsOut(amountIn, [a.address, wavax.address, b.address])[-1]

        amountInDecimals = amountIn/(10**a.decimals())
        amountOutDecimals = amountOut/(10**b.decimals())

        print(amountInDecimals, a.symbol(), ' -> ', amountOutDecimals, b.symbol())

        if (amountOutDecimals >= amountInDecimals * 1.01):
            try:
                # First make sure router can execute trade
                if a.allowance(user.address, router.address) < amountIn:
                    a.approve(router.address, amountIn, {'from':user.address})
                # execute trade
                router.swapExactTokensForTokens(amountIn, amountOut, [a.address, wavax.address, b.address],
                                                user.address, 1000*int(time.time()+35), {'from':user.address})
            except Exception as e:
                print('exception occured: ', e)
    time.sleep(10)
    pass

