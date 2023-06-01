
art = """


                   *    *      *    *     *     *       *
           *   *      *    *      *          *       *     *
                *  ____        *     *    *   ____ *   *      *
            *     |  _ \ _ __ _____  ___   _ / ___| ____    *
         *     *  | |_) | '__/ _ \ \/ / | | | |  _ / _  }      *
           *      |  __/| | | (_) >  <| |_| | |_| | (_) |   *
             *    |_|   |_|  \___/_/\_\__,  |\____|\____} *    *
          *     *           *          |___/
                       *        *                 *       *    *
           *   *    *    *   *    *     *      *     *      *
                 *    *        *      *     *     *       *
"""

print(art)



import time
import subprocess
import webbrowser

time.sleep(1.5) # Wait for 1.5 seconds

print("                  +=====================================+")
print("                 [||                                   ||]")
print("          +===[||[||  Starting TOR services for you... ||]||]===+")
print("                 [||                                   ||]")
print("                  +=====================================+")


subprocess.run(["sudo","systemctl","start","tor"])


time.sleep(1.5) # Wait for 1.5 seconds
print("                                          ")
print("                                [  DONE! ]")
print("                                          ")

time.sleep(2) # Wait for 2 seconds

# Get the status of tor service
result = subprocess.run(["sudo","systemctl","status","tor"], capture_output=True)

# Print the output of the command
print(result.stdout.decode())


time.sleep(.5) # Wait for .5 seconds
print("                                                                        ")
print("     * ============================================================== * ")
print("     *              Now starting PROXYCHAINS for you...               * ")
print("     * ============================================================== * ")
print("                                                                        ")
time.sleep(1) # Wait for 1 seconds

# Define the URL
url = "www.dnsleaktest.com"

# Run the proxychains command to open Firefox with the website
firefox_process = subprocess.Popen(["proxychains","firefox",url])

# Wait for firefox to exit
firefox_process.wait()


# Tor stop
subprocess.run(["sudo","systemctl","stop","tor"])


time.sleep(1) # Wait for 1 seconds
print("                                                                         ")
print("                                                                         ")
print("     * ============================================================== *  ")
print("   * * Firefox session has ENDED and Tor services have been DISABLED  * *")
print("     * ============================================================== *  ")

art = """

 +========================================================================+
 ||  _____ _              _          __                   _           _  ||
 || |_   _| |_  __ _ _ _ | |__ ___  / _|___ _ _   _  _ __(_)_ _  __ _| | ||
 ||   | | | ' \/ _` | ' \| / /(_-< |  _/ _ \ '_| | || (_-< | ' \/ _` |_| ||
 ||   |_| |_||_\__,_|_||_|_\_\/__/ |_| \___/_|    \_,_/__/_|_||_\__, (_) ||
 ||                                                              |___/   ||
 +========================================================================+

"""

print(art)
