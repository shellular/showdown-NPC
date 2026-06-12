import subprocess


#basic command running functionality
def runCommand(command):

    try:
        #send me your commands and we will send you output. remember it's just commands so it won't be much output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return "success", result.stdout

    #no idea what the difference between SubprocessError and CalledProcessError is but it can't hurt to have both
    except subprocess.CalledProcessError as e:
        print(f"you fucked up the command \"{e.cmd}\" and the code freaked out.\n\n Error: {e.stderr}\n(calledprocesserror)")
        return "ERROR_SPECIFIC", e.stderr

    except subprocess.SubprocessError as e:
        print(f"you fucked up the command \"{e}\" and the code freaked out. (subprocesserror)")
        return "ERROR_BROAD", e
    
    except FileNotFoundError:
        print(f"you don't own whatever you called here: \"{e}\". (filenotfounderror)")
        return "ERROR_NO_FILE", e