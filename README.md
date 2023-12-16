-------------------------------------------------------------------------------------------------------------------------------------------

# Proxygo - by TheJuicePapi

-------------------------------------------------------------------------------------------------------------------------------------------
![Screenshot_2023-06-01_19-32-16](https://github.com/TheJuicePapi/proxygo/assets/134894632/1e2e13fb-d436-4acf-bfd6-073829fba306)
![Screenshot_2023-06-01_19-32-54](https://github.com/TheJuicePapi/proxygo/assets/134894632/5598197e-7b0d-4c9f-9378-aac9bb3e5289)





DESCRIPTION

This is an automated python script to start tor services and then proxychains right after which will launch directly into a seperate firefox browser window.

Then after you are finished useing the program and you close the firefox browser window, The proxychains and tor services will be automatically disabled upon exiting the script.

* The install.sh will also make a shortcut so you can launch it from anywhere. 

-------------------------------
 
INSTALLATION & USAGE

Git clone installation:

1. 'sudo git clone https://github.com/TheJuicePapi/proxygo.git'
2. 'cd proxygo'
3. 'sudo chmod +x install.sh proxygo.py'
4. 'sudo ./install.sh'
5. 'sudo proxygo' (before using this command make sure to set up proxychains & tor files. See bellow for details)

-------------------------------

DEPENDANCIES

For this script to work you will need to have tor & proxychains installed. The install.sh should automatically install them for you.
If not then use 'sudo apt install tor && sudo apt install proxychains -y'

-------------------------------
CONFIGURATION

To set up proxychains...
Use 'sudo nano /etc/proxychains4.conf'
where it shows "#dynamic_chain" make sure to take the "#" away and then add a "#" to where it says "strict_chain".
By adding a "#" infront of "strict_chain" and taking it away from "dynamic_chain" it will force proxychains to use the dynamic proxy option instead.

Also scroll down and make sure "proxy_dns" is active, if not then activate it by taking away the "#" infront.

 Lastly scroll all the way to the bottom where you see "socks4  127.0.0.1 9050". Right under this line put "socks5  127.0.0.1 9050" 
 (This is your proxy list so you can also add in more proxy servers if you wish though imo there is not much of a need because dynamic proxychains already come with a list of servers that it will pick from. 

now we are finished setting up proxychains. There are many more things we can do here but for not let's just use this. 
To save press CTRL + X then Y and press then enter.

To set up tor services...
Use 'sudo su' then once in root 'cd' >>> 'cd /etc/tor' >>> 'nano torrc'
  Then scroll all the way to the bottom and insert "HTTPTunnelPort 8118"
  
  To save press CTRL + X then Y and press then enter.. Dont forget to restart tor after all this with 'sudo service tor restart'

Once done use 'proxygo' to start you should then be automatically directed to www.dnsleaktest.com in order to test 
if the proxychains are working correctly. 

  -------------------------------

This is my very first ever script / upload and has been tested on an RPI 4b running a kali linux arm.
Enjoy and use responsibly
