from replit import db
import discord
import os
import requests
from datetime import datetime



client = discord.Client()
WL = ["stride19uvw0azm9u0k6vqe4e22cga6kteskdqq3ulj6q"]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def microDenomToDenom(micro):
  return int(micro) / 10**6

def rateLimit(address):
    if address in WL:
        return False
    current_time = int(datetime.now().timestamp())
    if address not in db:
        db[address] = int(current_time)
        return False
    else:
        last_call = db[address]
        diff = current_time - last_call
        if diff < 86397:
            return True

ustrd_denom = "ustrd"
ibc_denom = "ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2"

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$balance'):
        try:
            _, addr = message.content.split(" ", 1)
            addr = addr.strip(' ')
        except Exception as e:
            print(e)
            await message.channel.send("Error: you must format your message as $balance stride19uvw0azm9u0k6vqe4e22cga6kteskdqq3ulj6q, using your address")
            return
        # STRD BALANCES
        d = requests.get(f"https://stride-node3.internal.stridenet.co:443/cosmos/bank/v1beta1/balances/{addr}/by_denom?denom={ustrd_denom}").json()
        micro = d['balance']['amount']
        strd = microDenomToDenom(micro)
        msg = f"balance for: {addr} is {strd} STRD"

        # IBC BALANCES
        d2 = requests.get(f"https://stride-node3.internal.stridenet.co:443/cosmos/bank/v1beta1/balances/{addr}/by_denom?denom={ibc_denom}").json()
        ibc_micro = d2['balance']['amount']
        ibc = microDenomToDenom(ibc_micro)
        msg2 = f"\nbalance for: {addr} is {ibc} ATOM on Stride"
        await message.channel.send(msg + msg2)

    elif message.content.startswith('$faucet'):
        try:
            _, addr = message.content.split(" ", 1)
            addr = addr.strip(' ')
        except Exception as e:
            print(e)
            await message.channel.send("Error: you must format your message as $faucet stride19uvw0azm9u0k6vqe4e22cga6kteskdqq3ulj6q, using your address")
            return
        # rate limit
        limit = rateLimit(addr)
        if limit:
            await message.channel.send(f'Please wait 24 hours to use the faucet')
            return
        else:
            # curl -X POST -d '{"address": "stride19uvw0azm9u0k6vqe4e22cga6kteskdqq3ulj6q"}' stride-node2.internal.stridenet.co:7936
            url = 'http://stride-node2.internal.stridenet.co:27936'
            myobj = {'address': f'{addr}'}
            x = requests.post(url, json = myobj)
            msg = x.status_code
            if msg == 200:
                await message.channel.send(f'Sent 10 STRD and 10 ATOM to {addr}, {msg}')
            else:
                print(x)
                await message.channel.send(f'Failed to send STRD, the faucet might be down or you\'ve hit your faucet limit.')
    else:
        await message.channel.send(f'Query your balance or request tokens, every 24 hours. Commands are \n\t $balance <address> \n\t $faucet <address>')

my_secret = os.environ['TOKEN']
client.run(my_secret)
