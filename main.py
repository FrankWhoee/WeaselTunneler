import json
import time

import yaml
import discord
import requests
import os
import sys
from subprocess import Popen, PIPE

tries = 10

serverp = ...  # type: Popen

client = discord.Client()

if os.path.exists("config"):
    with open('config', 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    print("[WARN] No configuration file found.")
    token = input("Give a token or give an empty string to replace it later:\n")
    with open('config', 'w') as file:
        config = {
            "token": token
        }
        file.write(yaml.dump(config))
    print("[WARN] A new configuration file has been created at config.")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def createNgrok():
    try:
        # print(requests.get('http://localhost:4040/api/tunnels').text)
        response = json.loads(requests.get('http://localhost:4040/api/tunnels', verify=False).text)

        pub_url = response['tunnels'][0]['public_url']
    except Exception as bige:
        print(bige)
        p = Popen("exec " + "./ngrok tcp 22", shell=True)
        i = 0
        while (True):
            try:
                time.sleep(1)
                response = Popen("exec " + "curl http://localhost:4040/api/tunnels", shell=True, stdout=PIPE).communicate()[0]
                response = json.loads(response.decode("utf-8"))
                pub_url = response['tunnels'][0]['public_url']
                break
            except Exception as e:
                print(e)
                print(f"Attempting ngrok connection again... ({i})")
                i += 1
                if i > 1:
                    return "Failed to create ngrok tunnel."
    return pub_url.replace("tcp://", "")


def killNgrok():
    p = Popen("exec " + "killall ngrok", shell=True)


@client.event
async def on_message(message):
    # 420468092108406785 is my personal testing channel ID
    if message.author == client.user:
        return
    if not message.content.startswith(";"):
        return
    command = message.content.split(" ")[0]
    param = message.content.split(" ")[1:]
    command = command[1:]

    if command == "ngrok" or command == "ip":
        response_text = """
                {0.author.mention}\nPublic URL: {1}
                """.format(message, createNgrok())
        await message.channel.send(response_text)
    elif command == "kill" or command == "close":
        killNgrok()
        await message.channel.send("All ngrok instances on this machine was killed.")

while (tries > 0):
    try:
        client.run(config["token"])
        break
    except:
        time.sleep(1)
