from . import basicFunctionUtil
import pathlib
import webbrowser

def initNPMCheck():
    commandRanResult = basicFunctionUtil.runCommand("npm help", True, None, False, False, False, False)
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
        if not pathlib.Path("showdownInstall/pokemon-showdown").exists():
            #takes it from the git repo
            basicFunctionUtil.runCommand("git clone https://github.com/smogon/pokemon-showdown.git", True, "showdownInstall", False, False)
        return "SUCCESS"


def launchServer():
    basicFunctionUtil.runCommand("node pokemon-showdown 8000", True, "showdownInstall/pokemon-showdown", True)

def launchSite():
    webbrowser.open("http://localhost:8000")

def fullHousekeeping():

    installState = tryInstallShowdown()

    if installState == "SUCCESS":

        if pathlib.Path("showdownInstall/pokemon-showdown").exists():
            launchServer()
            input("server up! press enter to continue\n")
            launchSite()