import json
import yaml
import discord
import requests
import os
import sys
from subprocess import Popen, PIPE

serverp = ... # type: Popen

client = discord.Client()

if os.path.exists("config"):
    with open('config', 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    print("[WARN] No configuration file found.")
    with open('config', 'w') as file:
        config = {
            "token": "REPLACE_WITH_YOUR_TOKEN"
        }
        yaml.dump(config)
    print("[WARN] A new configuration file has been created at config.")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

def createNgrok():
    try:
        response = json.loads(requests.get('http://localhost:4040/api/tunnels').text)
        pub_url = response['tunnels'][0]['public_url']
    except:
        p = Popen("exec " + "ngrok tcp 22", shell=True)
        while (True):
            try:
                response = json.loads(requests.get('http://localhost:4040/api/tunnels').text)
                pub_url = response['tunnels'][0]['public_url']
                break
            except Exception as e:
                print("Attempting ngrok connection again...")
    return pub_url.replace("tcp://","")

@client.event
async def on_message(message):
    # 420468092108406785 is my personal testing channel ID
    if message.author == client.user or (message.channel.id != config["channel"] or message.channel.id != 420468092108406785):
        return

    command = message.content.split(" ")[0]
    param = message.content.split(" ")[1:]
    command = command[1:]

    if command == "ngrok" or command == "ip":
        response_text = """
                {0.author.mention}\nPublic URL: {1}
                """.format(message, createNgrok())
        await message.channel.send(response_text)


client.run(config["token"])