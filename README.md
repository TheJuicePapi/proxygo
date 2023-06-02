-------------------------------------------------------------------------------------------------------------------------------------------

# Proxygo - by TheJuicePapi

-------------------------------------------------------------------------------------------------------------------------------------------
![Screenshot_2023-06-01_19-32-16](https://github.com/TheJuicePapi/proxygo/assets/134894632/1e2e13fb-d436-4acf-bfd6-073829fba306)
![Screenshot_2023-06-01_19-32-54](https://github.com/TheJuicePapi/proxygo/assets/134894632/5598197e-7b0d-4c9f-9378-aac9bb3e5289)





DEPENDANCIES

You will need to have previously installed tor services, if not use: 'sudo apt-get install tor'
You will also need to have installed proxychains, if not use: 'sudo apt-get install proxychains'

*** Dont forget to configure both tor & proxychains configuration files when first installing them ***
-------------------------------

DESCRIPTION

This is an automated python script to start tor services and then proxychains right after which will launch directly into a seperate firefox browser window.

Then after you are finished and you close the firefox browser window, The proxychains and the tor services will be automatically disabled upon exiting the script.

-------------------------------
 
INSTALLATION & USAGE

You can download using either git clone or by chosing the zip folder option.

For git clone installation:

1. 'sudo git clone https://github.com/TheJuicePapi/proxygo.git'
2. 'cd proxygo'
3. 'python3 proxygo.py'

For manual zip / raw file installation:

Simply download the file then copy and paste or move the python script into the desired location.
Then once in the directory run the script using 'python3 proxygo.py'

Once run you should then be automatically directed to www.dnsleaktest.com in order to test 
if the proxychains are working correctly. 

-------------------------------

This is my very first ever script / upload and has been tested on an RPI 4b running a kali linux arm. 
