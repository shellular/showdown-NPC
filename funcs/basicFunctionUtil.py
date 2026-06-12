import subprocess
import json



def readFile(fileDirectoryFromBaseFolder):

    #read the thing
    try:
        with open(fileDirectoryFromBaseFolder, "r") as fileInQuestion:
            fileRead = fileInQuestion.read()

        #first return is success, second is output
        return True, fileRead
    
    #Exception just seemed to be saying vaguely what fucked up
    except Exception as e:
        print(f"something fucked up with the file reading ({e})")
        return False, "ERROR"



#0 is to load full file, 1 is to return value, 2 creates a dump
def manageJSON(fileDirectoryFromBaseFolder, typeToReturn = 0, dictValue = "placeholderDictValue"):

    fileReadSuccess, fileOutput = readFile(fileDirectoryFromBaseFolder)

    #checks if readFile threw an error and only does the thing if it didn't
    if fileReadSuccess:


        loadedFileAsJSON = json.loads(fileOutput)
        #if it becomes a dictionary, do that
        if typeToReturn == 0:
            #load the text we just read and send it back as a dict
            return loadedFileAsJSON
        
        elif typeToReturn == 1:
            #load the text we just read and send it back as a dict. if it's not there then get pissed
            try:
                return loadedFileAsJSON[dictValue]
            
            except:
                print("dunno what you sent but it wasn't a dictValue")
                return None

        elif typeToReturn == 2:
            #pretty self explanatory. you do a little dump
            return json.dumps(loadedFileAsJSON)
        
        else:
            print("i dunno what you tried to do here but you didn't send the right type to return")
            return None
        

    elif not fileReadSuccess:
            print(f"couldn't read file {fileDirectoryFromBaseFolder}")
    
        

#basic command running functionality
def runCommand(command):

    try:
        #send me your commands and we will send you output. remember it's just commands so it won't be much output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return "SUCCESS", result.stdout

    #no idea what the difference between SubprocessError and CalledProcessError beyond SubprocessError being the catch-all is but it can't hurt to have both
    except subprocess.CalledProcessError as e:
        print(f"you fucked up the command \"{e.cmd}\" and the code freaked out.\n\n Error: {e.stderr}\n(calledprocesserror)")
        return "ERROR_SPECIFIC", e.stderr

    except FileNotFoundError:
        print(f"you don't own whatever you called here. (filenotfounderror)")
        return "ERROR_NO_FILE", "empty"
    
    except subprocess.SubprocessError as e:
        print(f"you fucked up the command \"{e}\" and the code freaked out. (subprocesserror)")
        return "ERROR_BROAD", str(e)
    
    