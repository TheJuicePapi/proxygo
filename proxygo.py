#!/usr/bin/env python3

from termcolor import colored, cprint
import os
import time
import subprocess
import webbrowser

# Function to clear the screen
def clear_screen():
    os.system('clear')

# ASCII Art with color
art = colored("""

                   *    *      *    *     *     *       *
           *   *      *    *      *          *       *     *
                *  ____        *     *    *   ____ *   *      *
            *     |  _ \ _ __ _____  ___   _ / ___| ____    *
               *  | |_) | '__/ _ \ \/ / | | | |  _ / _  }      *
           *      |  __/| | | (_) >  <| |_| | |_| | (_) |   *
             *    |_|   |_|  \___/_/\_\__,  |\____|\____} *    *
          *     *           *          |___/
                       *        *                 *       *    *
           *   *    *    *   *    *     *      *     *      *
                 *    *        *      *     *     *       *
""", 'cyan')

try:
    clear_screen()
    cprint(art, attrs=['bold'])

    time.sleep(1.5)  # Wait for 1.5 seconds

    # Print header with color
    header = colored("                  +=====================================+", 'yellow', attrs=['bold'])
    cprint(header) 
    cprint("                 [||                                   ||]", 'yellow')
    cprint("          +===[||[||  Starting TOR services for you... ||]||]===+", 'yellow', attrs=['bold'])
    cprint("                 [||                                   ||]", 'yellow')
    cprint("                  +=====================================+", 'yellow', attrs=['bold'])

    # Start TOR services
    subprocess.run(["sudo", "systemctl", "start", "tor"])

    time.sleep(1.5)  # Wait for 1.5 seconds
    print("                                           ")
    cprint("                                [  DONE! ]", 'green', attrs=['bold'])
    print("                                           ")

    time.sleep(2)  # Wait for 2 seconds

    # Get the status of tor service
    result = subprocess.run(["sudo", "systemctl", "status", "tor"], capture_output=True)

    # Print the output of the command
    status_output = result.stdout.decode()
    if status_output:
        clear_screen()
        cprint(status_output, 'white')
    else:
        cprint("Error retrieving the TOR status.", 'red', attrs=['bold'])

    time.sleep(.5)  # Wait for .5 seconds
    clear_screen()
    cprint("                                                                        ", 'yellow')
    cprint("     * ============================================================== * ", 'yellow')
    cprint("     *              Now starting PROXYCHAINS for you...               * ", 'yellow')
    cprint("     * ============================================================== * ", 'yellow')
    print("                                                                        ")

    time.sleep(1)  # Wait for 1 second

    # Define the URL
    url = "http://www.dnsleaktest.com"

    try:
        # Run the proxychains command to open Firefox with the website
        firefox_process = subprocess.Popen(["proxychains", "firefox", url])
        
        try:
            # Wait for Firefox to exit
            firefox_process.wait()
        except KeyboardInterrupt:
            # Handle interruption
            cprint("\nFirefox session interrupted by user. Stopping TOR services...", 'red', attrs=['bold'])
            # Ensure the TOR service is stopped
            subprocess.run(["sudo", "systemctl", "stop", "tor"])
            # Exit the script
            exit(1)
        
    except Exception as e:
        cprint(f"Failed to launch Firefox: {str(e)}", 'red', attrs=['bold'])
        
    finally:
        # Stop TOR services
        subprocess.run(["sudo", "systemctl", "stop", "tor"])

        time.sleep(1)  # Wait for 1 second
        clear_screen()
        cprint("                                                                      ", 'yellow')
        cprint("     * ============================================================== *  ", 'red')
        cprint("   * * Firefox session has ENDED and Tor services have been DISABLED  * *", 'red', attrs=['bold'])
        cprint("     * ============================================================== *  ", 'red')

        # Final art with color
        final_art = colored("""
 +========================================================================+
 ||  _____ _              _          __                   _           _  ||
 || |_   _| |_  __ _ _ _ | |__ ___  / _|___ _ _   _  _ __(_)_ _  __ _| | ||
 ||   | | | ' \/ _` | ' \| / /(_-< |  _/ _ \ '_| | || (_-< | ' \/ _` |_| ||
 ||   |_| |_||_\__,_|_||_|_\_\/__/ |_| \___/_|    \_,_/__/_|_||_\__, (_) ||
 ||                                                              |___/   ||
 +========================================================================+
""", 'cyan')

        cprint(final_art, attrs=['bold'])
        
except KeyboardInterrupt:
    # Handle interruption at the top level
    cprint("\nScript interrupted by user. Stopping TOR services...", 'red', attrs=['bold'])
    subprocess.run(["sudo", "systemctl", "stop", "tor"])
    exit(1)
