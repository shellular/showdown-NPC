import basicFunctionUtil
import pathlib

def initNPMCheck():
    commandRanResult = basicFunctionUtil.runCommand("npm help")
    #apparently you can send back a logic statement and it'll end up as a true/false bool. neato
    return commandRanResult["endResult"] == "SUCCESS"

def tryInstallShowdown():
    hasNPM = initNPMCheck()
    if not hasNPM:
        print("you don't have NPM but i really need that. this is gonna throw some kinda error. i'll probably put a winget thingy here later but for now just go download nodejs and NPM")
        return "NPM_ERROR"
    else:
        #make path showdownInstall if it does not exist
        pathlib.Path("showdownInstall").mkdir(parents=True, exist_ok=True)
        #clones showdown into folder
        basicFunctionUtil.runCommand("git clone https://github.com/smogon/pokemon-showdown.git", True, "showdownInstall")
        return "SUCCESS"

def launchServer():
    basicFunctionUtil.runCommand("node pokemon-showdown 8000", True, "showdownInstall/Pokemon-Showdown")