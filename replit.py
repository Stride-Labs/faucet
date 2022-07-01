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
        d = requests.get(f"http://stride-node3.internal.stridenet.co:1317/cosmos/bank/v1beta1/balances/{addr}/by_denom?denom=ustrd").json()
        micro = d['balance']['amount']
        strd = microDenomToDenom(micro)
        msg = f"balance for: {addr} is {strd} STRD"
        await message.channel.send(msg)

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
            # curl -X POST -d '{"address": "stride19uvw0azm9u0k6vqe4e22cga6kteskdqq3ulj6q"}' stride-node2.internal.stridenet.co:8000
            url = 'http://stride-node2.internal.stridenet.co:8000'
            myobj = {'address': f'{addr}'}
            x = requests.post(url, json = myobj)
            msg = x.status_code
            if msg == "200":
                await message.channel.send(f'Sent 10 STRD to {addr}, {msg}')
            else:
                await message.channel.send(f'Failed to send STRD, faucet is down!')
    else:
        await message.channel.send(f'Query your balance or request tokens, every 24 hours. Commands are \n\t $balance <address> \n\t $faucet <address>')

my_secret = os.environ['TOKEN']
client.run(my_secret)
