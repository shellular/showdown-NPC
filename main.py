import os
import subprocess
import asyncio
import poke_env
from poke_env.player import RandomPlayer
from poke_env import AccountConfiguration, ShowdownServerConfiguration
from funcs import basicFunctionUtil
from funcs import serverLoad

botToFight = ""
botInfo = None

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

    print(f"Bot Name: {botInfo["name"]}")

    serverLoad.fullHousekeeping()
    #Sits for a bit for the server to start up
    await asyncio.sleep(5)
    serverLoad.launchSite()

    bot = RandomPlayer(
        account_configuration=AccountConfiguration(botInfo["name"], "password"),
        max_concurrent_battles=1
    )
    
    await bot.accept_challenges(None, 1)

asyncio.run(main())