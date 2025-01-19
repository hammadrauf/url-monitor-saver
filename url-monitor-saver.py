#!/usr/bin/python3
# https://pyinstaller.org/en/stable/spec-files.html#using-spec-files
## Install
# - pip install pyyaml, pywin32
# - pip install pywebview, pynput
#
import threading
from pynput import keyboard, mouse
import time
import os
import sys
import yaml
import hashlib
import win32con
import win32api
import ctypes
import webview

config_file_name = 'config-url-monitor-saver.yml'
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_file_path = os.path.join(application_path, config_file_name)

'''
Author: Hammad Rauf (rauf.hammad@gmail.com)
License: MIT (Open Source, Free)
Description:
Monitors a URL in Default Browser and Act As a Screen saver turning off monitor frequently
and turning back on again. The URL and intervals for Screen-ON and Screen-Off are to be
given in as YAML text config file. This YAML file should be in the same folder as the executable
file.
ZoneMinder article: https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/
screen_Off function is only for Windows based computers.
Sample YAML file contents:
---
  domain: "zoneminder.xyz.com"
  secret_key: "SomeRandomSecretKey-FromZoneMinder-Options"
  username: "SomeUserName"
  password_hash: "PasswordHash-From-MySQLDB-table-zoneminder"
  seconds_off: 5
  seconds_on: 8
  frame_width: 1024
  frame_height: 1000
  screenoff_enabled: False                                                     
'''

config={}
try:   
    with open(config_file_path) as stream:
        try:
            config=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
except:
    print(f"Config file not found at location: {config_file_path}")
    sys.exit(1)

domain=config['domain']
#base_url = f"https://{domain}/index.php?view=watch&mid=1&auth="
base_url=f"https://{domain}/index.php?view=montage&group=1&scale=0.5&auth="
secret_key = config['secret_key']
username = config['username']
password_hash = config['password_hash']
seconds_off = config['seconds_off']
seconds_on = config['seconds_on']
frame_width = config['frame_width']
frame_height = config['frame_height']
screenoff_enabled = config['screenoff_enabled']

def generate_auth_hash(use_remote_addr, uname=username, pwd_hash=password_hash, remote_address=domain, zm_auth_secret=secret_key):
    current_time = time.localtime()
    #print(f'User Name: {uname}')
    #print(f"time-string is = {format(current_time.tm_hour) + format(current_time.tm_mday) + format(current_time.tm_mon-1) + format(current_time.tm_year-1900)}")
    if use_remote_addr:
        auth_key = (zm_auth_secret + 
                    uname + 
                    pwd_hash + 
                    remote_address + 
                    format(current_time.tm_hour) +
                    format(current_time.tm_mday) +
                    format(current_time.tm_mon-1) +
                    format(current_time.tm_year-1900))
    else:
        auth_key = (zm_auth_secret + 
                    uname + 
                    pwd_hash + 
                    format(current_time.tm_hour) +
                    format(current_time.tm_mday) +
                    format(current_time.tm_mon-1) +
                    format(current_time.tm_year-1900))
    auth = hashlib.md5(auth_key.encode()).hexdigest()
    return auth

def screenOff():
    if screenoff_enabled:
        ctypes.windll.user32.SendMessageW(65535, 274, 61808, 2)
def screenOn():
    if screenoff_enabled:
        ctypes.windll.user32.SendMessageW(65535, 274, 61808, -1)
        moveCursor()
def moveCursor():
    x, y = (0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y)

# Generate the URL with Authentication for Display
authenticated_url = base_url+generate_auth_hash(False)

# Event to control the main loop and listeners
terminate_event = threading.Event()

def destroy(window, timeInSec):
    for _ in range(timeInSec):
        if terminate_event.is_set():
            break
        time.sleep(1)
    window.destroy()

def on_key_event(key):
    terminate_event.set()
    return False

def on_mouse_event(x, y):
    terminate_event.set()
    return False

def keypress_listener():
    with keyboard.Listener(on_press=on_key_event) as listener:
        listener.join()

def mouse_listener():
    with mouse.Listener(on_move=on_mouse_event) as listener:
        listener.join()

# Create and start the keypress and mouse listener threads
keyboard_listenerO = keyboard.Listener(on_press=on_key_event)
mouse_listenerO = mouse.Listener(on_move=on_mouse_event)
keyboard_thread = threading.Thread(target=keyboard_listenerO.start)
mouse_thread = threading.Thread(target=mouse_listenerO.start)
keyboard_thread.start()
mouse_thread.start()

# Main program code
while not terminate_event.is_set():
    screenOn()
    mywin = webview.create_window('ZoneMinder', authenticated_url, width=frame_width, height=frame_height)
    webview.start(destroy, (mywin, seconds_on))
    if terminate_event.is_set():
        screenOn()
        break
    
    screenOff()
    for _ in range(seconds_off):
        if terminate_event.is_set():
            screenOn()
            break
        time.sleep(1)    

# Stop the listeners if the program is terminating
keyboard_listenerO.stop()
mouse_listenerO.stop()

# Wait for the threads to finish
keyboard_thread.join()
mouse_thread.join()
# if adding threads, then join them here.

# end.
