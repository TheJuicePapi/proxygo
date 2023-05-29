-------------------------------------------------------------------------------------------------------------------------------------------

# Proxygo - by TheJuicePapi

-------------------------------------------------------------------------------------------------------------------------------------------
![Screenshot_2023-05-29_15-23-14](https://github.com/TheJuicePapi/proxygo/assets/134894632/c973f808-5405-466e-b4cb-b00c983e0d48)

![Screenshot_2023-05-29_15-23-31](https://github.com/TheJuicePapi/proxygo/assets/134894632/43d29973-9406-4abe-8962-9f29edfbaafa)


DEPENDANCIES

You will need to have previously installed tor services, if not use: 'sudo apt-get install tor'
You will also need to have installed proxychains, if not use: 'sudo apt-get install proxychains'

*** Dont forget to configure both tor & proxychains configuration files when first installing them ***
-------------------------------

DESCRIPTION

This is an automated python script to start tor services and then proxychains right after that will launch directly into a seperate firefox browser window.

Then after you are finished and you close the firefox browser window, The proxychains and then the tor services will be automatically disabled upon exiting the script.

-------------------------------
 
INSTALLATION & USAGE

Simply download the script file and place it in your /home/usr directory folder.

Then to launch simply open a terimal and use 'python3 proxygo.py'

You should then be automatically directed to www.dnsleaktest.com in order to test 
if the proxychains are working correctly. 

-------------------------------

This is my very first ever script / upload and has been tested on an RPI 4b running a kali linux arm. 
