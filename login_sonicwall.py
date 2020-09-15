# from def_funtions import (setup_session, login, persist, update_rem_time,keep_alive)
'''I have modified this code for my schools use. The code did not function as
advertised so I changed a few funtions and how the main executes so it provides
constant access to wifi as long as the program is open.

BSD 3-Clause License

Copyright (c) 2017, Shubham Sopan Dighe
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import time
import re
from hashlib import md5
import requests
from html.parser import HTMLParser
import os
import sys
import logging
import json
import getpass
import errno
from string import digits
from hashlib import md5
import random
import urllib3

# Removes insecure https connection error
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Reads file with credentials and processes them for login
file = open("credentials.txt", "r")
cred_unproc = ''
for word in file.readlines():
    cred_unproc += word.strip("\n")
file.close()

cred = cred_unproc.split(" ")
UNAME = cred[0]
PASSWORD = cred[1]
print(f"[+] Logging In as: {UNAME}")


BEAT_INTERVAL = 15
MIN_RELOGIN = 10

DOMAIN = 'https://10.20.51.1/'

def snooze(factor):
    ONE_MINUTE = 60
    time.sleep(ONE_MINUTE * factor)

def generate_cookie():
    seed = ''.join(random.choice(digits) for _ in range(16))
    value = md5(seed.encode()).hexdigest()
    return value

def is_logged_in(response):
    if "refresh=true" in response.text:
        return False
    return True

def remaining_time(response):
    time = 0
    pos = response.text.find("remTime=")
    if pos != -1:
        time = response.text[pos+8:pos+11]
        time = time.split(';')[0]
        try:
            time = int(time)
        except ValueError:
            time = 0;
    return time

def set_cookies(session):
    domain = '10.20.51.1'
    session.cookies.set(name='SessId', value=generate_cookie().upper(), domain=domain)
    session.cookies.set(name='PageSeed', value=generate_cookie(), domain=domain)

def read_credentials():
    print("\n[+] Reading credentials ...")

    creds = {}
    creds['uName'] = [UNAME]
    creds['pass'] = [PASSWORD]
    return creds

def login(session):
    payload = read_credentials()
    print("[+] Authenticating with SonicWall ...")
    login_attempt = 6

    while login_attempt > 0:
        t = session.get(DOMAIN + 'auth1.html')
        t = session.post(DOMAIN +'auth.cgi', data=payload)
        session.get(DOMAIN  + "loginStatusTop(eng).html")
        t = session.post(DOMAIN  + "usrHeartbeat.cgi", verify=False)

        if is_logged_in(t):
            print("[+] Logged in successfully !!  :)")
            current_time = time.strftime("%H:%M:%S  %d-%m-%Y", time.localtime())
            print("[+] Login time :- %s " % current_time)
            print("[+] (Keep this window open for a persistent connection and minimize it.)")
            return True
        else:
            login_attempt -= 1

    print("[-] Login failed !!  :( \n")
    return False


def persist(session):
    logged_in = True
    while logged_in:
        try:
            t = session.post(DOMAIN + "usrHeartbeat.cgi", verify=False)
            logged_in = is_logged_in(t)
            rem_time = remaining_time(t)
            if rem_time <= 30:
                print("\n[*] Session will expire soon. Logging in again ...")
                set_cookies(session)
                logged_in = login(session)
            else:
                snooze(5)

        except (requests.exceptions.ConnectionError):
            snooze(1)

    print("[-] Seems like something went wrong !!")
    print("[-] You have been logged out of SonicWall Wifi portal.")


def setup_session():
    s = requests.Session()
    http_adapter = requests.adapters.HTTPAdapter(max_retries=6)
    https_adapter = requests.adapters.HTTPAdapter(max_retries=6)
    s.mount('http://', http_adapter)
    s.mount('https://', https_adapter)
    s.verify = False
    set_cookies(s)
    return s

def keep_alive(session):
    logged_in = True
    while logged_in:
        try:
            t = session.post(DOMAIN + "usrHeartbeat.cgi", verify=False)
            logged_in = is_logged_in(t)
            if logged_in:
                snooze(5)

        except (requests.exceptions.ConnectionError):
            snooze(1)
    print("[+] You have been logged out of Dell SonicWall")

def update_rem_time(session, rem_time):
    if rem_time <=0:
        rem_time = 1
    payload = {'maxSessionTime': rem_time}
    t = session.post(DOMAIN + 'userSettings.cgi', data=payload)
    session.post(DOMAIN + "usrHeartbeat.cgi", verify=False)

def main():
    while True:
        print("[+] Logging in for 85 min. You will be automtaically relogged in at the end of the 85 min. To disconnect, Exit this window.")
        print("[*] By running this program, you agree that the author will not be held responsible if there is a malfunction (in middle of a zoom class).")
        session = setup_session()
        login_time = 85
        if login(session):
            try:
                if login_time:
                    update_rem_time(session, login_time)
                    keep_alive(session)

                else:

                    persist(session)
                    print("[+] Setting up Session")


            except KeyboardInterrupt:
                print("\n[-] Exiting ...\n")


main()