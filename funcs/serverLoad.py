import basicFunctionUtil

def initNPMCheck():
    commandRanResult = basicFunctionUtil.runCommand("npm help")
    #apparently you can send back a logic statement and it'll end up as a true/false bool. neato
    return commandRanResult["endResult"] == "SUCCESS"

def housekeeping():
    hasNPM = initNPMCheck()
    if not hasNPM:
        print("you don't have NPM but i really need that. this is gonna throw some kinda error. i'll probably put a winget thingy here later but for now just go download nodejs and NPM")
    
    