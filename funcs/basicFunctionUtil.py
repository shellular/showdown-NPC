import subprocess
import json

def ping():
     print("pong")


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




def loadFileAsJSON(fileDirectoryFromBaseFolder):

    fileReadSuccess, fileOutput = readFile(fileDirectoryFromBaseFolder)
    #checks if readFile threw an error and only does the thing if it didn't
    if fileReadSuccess:

        loadedFileAsJSON = json.loads(fileOutput)
        #load the text we just read and send it back as a dict
        return loadedFileAsJSON
        

    elif not fileReadSuccess:
            print(f"couldn't read file {fileDirectoryFromBaseFolder}")




def grabValueFromJSON(fileDirectoryFromBaseFolder, dictValue):

    fileReadSuccess, fileOutput = readFile(fileDirectoryFromBaseFolder)
    if fileReadSuccess:

        try:
            loadedFileAsJSON = json.loads(fileOutput)
            return loadedFileAsJSON[dictValue]
        
        except:
            print("dunno what you sent but it wasn't a dictValue")
            return None
        
        
    elif not fileReadSuccess:
            print(f"couldn't read file {fileDirectoryFromBaseFolder}")




def dumpJSON(fileDirectoryFromBaseFolder):

    fileReadSuccess, fileOutput = readFile(fileDirectoryFromBaseFolder)
    if fileReadSuccess:

        loadedFileAsJSON = json.loads(fileOutput)
        return json.dumps(loadedFileAsJSON)     

    elif not fileReadSuccess:
            print(f"couldn't read file {fileDirectoryFromBaseFolder}")
    
        

#basic command running functionality. apparently cwd specifies where to put stuff
def runCommand(command, useShell, cwdUsed=None, popen=False, capture_output=True, text=True, check=True, stdoutSent=True):
    if not popen:
        try:
            #send me your commands and we will send you output. remember it's just commands so it won't be much output
            result = subprocess.run(command, capture_output=capture_output, text=text, check=check, shell=useShell, cwd=cwdUsed)
            if capture_output:
                return {"endResult": "SUCCESS", "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
            else:
                return {"endResult": "SUCCESS", "stdout": None, "stderr": None, "returncode": result.returncode}

        #no idea what the difference between SubprocessError and CalledProcessError beyond SubprocessError being the catch-all is but it can't hurt to have both
        except subprocess.CalledProcessError as e:
            return {"endResult": "ERROR_SPECIFIC", "stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode}

        except FileNotFoundError as e:
            return {"endResult": "ERROR_NO_FILE", "stdout": None, "stderr": str(e), "returncode": None}
        
        except subprocess.SubprocessError as e:
            return {"endResult": "ERROR_BROAD", "stdout": None, "stderr": str(e), "returncode": None}
    else:
        subprocess.Popen(command, shell=useShell, cwd=cwdUsed)
        return {"endResult": "STARTED_P",  "stdout": None, "stderr": None, "returncode": None}

