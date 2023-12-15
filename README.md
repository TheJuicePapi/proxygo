-------------------------------------------------------------------------------------------------------------------------------------------

# Proxygo - by TheJuicePapi

-------------------------------------------------------------------------------------------------------------------------------------------
![Screenshot_2023-06-01_19-32-16](https://github.com/TheJuicePapi/proxygo/assets/134894632/1e2e13fb-d436-4acf-bfd6-073829fba306)
![Screenshot_2023-06-01_19-32-54](https://github.com/TheJuicePapi/proxygo/assets/134894632/5598197e-7b0d-4c9f-9378-aac9bb3e5289)





DESCRIPTION

This is an automated python script to start tor services and then proxychains right after which will launch directly into a seperate firefox browser window.

Then after you are finished and you close the firefox browser window, The proxychains and the tor services will be automatically disabled upon exiting the script.

The install.sh will also make a shortcut so you can launch it from anywhere.

-------------------------------
 
INSTALLATION & USAGE

For git clone installation:

1. 'git clone https://github.com/TheJuicePapi/proxygo.git'
2. 'cd proxygo'
3. 'chmod +x install.sh'
4. 'sudo ./install.sh'
5. 'proxygo' (before using this command make sure to set up proxychains & tor files. See bellow for details)

Once it's all set up and run you should then be automatically directed to www.dnsleaktest.com in order to test 
if the proxychains are working correctly. 

-------------------------------

DEPENDANCIES

For this script to work you will need to have tor & proxychains installed. The install.sh should automatically install them for you.
If not then use 'sudo apt install tor && sudo apt install proxychains -y'

-------------------------------
CONFIGURATION

Now to configure the files...
To set up proxychains use 'sudo nano /etc/proxychains4.conf'
where it shows "#dynamic_chain" make sure to take the "#" away and then add a "#" to where it says "strict_chain".
By adding a "#" infront of "strict_chain" and taking it away from "dynamic_chain" it will force proxychains to use the dynamic proxy option instead.

Also scroll down and make sure "proxy_dns" is active, if not then activate it by taking away the "#" infront.

 Lastly scroll all the way to the bottom where you see "socks4  127.0.0.1 9050". Right under this line write in "socks5  127.0.0.1 9050" so it now looks like:
socks4  127.0.0.1 9050
socks5  127.0.0.1 9050

now we are finished setting up proxychains. There are many more things we can do here but for not let's just use this. 
To save press CTRL + X then Y and press then enter.

Now to set up tor... 

-------------------------------


This is my very first ever script / upload and has been tested on an RPI 4b running a kali linux arm. 
