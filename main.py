import os
import subprocess
import asyncio
import poke_env
from poke_env.player import RandomPlayer
from poke_env import AccountConfiguration
from poke_env import ServerConfiguration
from funcs import basicFunctionUtil
from funcs import serverLoad

botToFight = ""
botInfo = None
bot = None

async def main():
    global botToFight, botInfo
    basicFunctionUtil.ping()

    #while we don't have the bot, try to get and load it and if it doesn't work repeat the process
    while not botInfo:
        botToFight = input("please type the name of the configured bot you'd like to fight.\n")
        botInfo = basicFunctionUtil.loadFileAsJSON(f"./bots/{botToFight}.json")
        if botInfo:
            print(f"Bot found!")
        else:
            print("you messed up LOL")

    print(f"bot Name: {botInfo["name"]}")

    serverLoad.fullHousekeeping()
    #Sits for a bit for the server to start up
    await asyncio.sleep(5)
    serverLoad.launchSite()
    
    #tries to open the bot and kills everything if it fails
    try:
        
        bot = RandomPlayer(
            avatar=botInfo["avatar"],
            account_configuration=AccountConfiguration(botInfo["name"], None),
            max_concurrent_battles=1
        )
        print("bot initialized!\n\n")
    except Exception as e:
        print(f"the bot couldn't be initialized. \n{str(e)}")
        return
        
    print("\nThe bot's now looking to accept a fight. Here's how to fight it:" \
    "\n1. Choose a name in the top right. If it's taken, choose a different name." \
    f"\n2. Click \"Find a User\" on the left, then search \"{botInfo["name"]}\"." \
    "Click \"Challenge\" under their profile, and set the challenge to be a Random Battle (it's that by default.) They should accept.")

    await bot.accept_challenges(None, 1)

asyncio.run(main())