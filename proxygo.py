
art = """

 ____                       ____
|  _ \ _ __ _____  ___   _ / ___| ____
| |_) | '__/ _ \ \/ / | | | |  _ / _  }
|  __/| | | (_) >  <| |_| | |_| | (_) |
|_|   |_|  \___/_/\_\__,  |\____|\____}
                     |___/
"""

print(art)



import time 

time.sleep(1.5) # Wait for 1.5 seconds
print("starting tor services...")

import subprocess

subprocess.run(["sudo","systemctl","start","tor"])

import time 

time.sleep(1.5) # Wait for 1.5 seconds
print("done!")

import time
import subprocess

time.sleep(2) # Wait for 2 seconds

# Get the status of tor service
result = subprocess.run(["sudo","systemctl","status","tor"], capture_output=True)

# Print the output of the command
print(result.stdout.decode())

import time 

time.sleep(1) # Wait for 1 seconds
print("Now starting proxychains for you...")




import subprocess
import webbrowser

# Define the URL
url = "www.dnsleaktest.com"

# Run the proxychains command to open Firefox with the website
firefox_process = subprocess.Popen(["proxychains","firefox",url])

# Wait for firefox to exit
firefox_process.wait()


# Tor stop
subprocess.run(["sudo","systemctl","stop","tor"])

import time 

time.sleep(1) # Wait for 1 seconds
print("Firefox has exited and tor services have been disabled...")





