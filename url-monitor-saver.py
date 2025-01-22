#!/usr/bin/python3
# https://pyinstaller.org/en/stable/spec-files.html#using-spec-files
## Install
# - pip install pyyaml
# - pip install pywebview, pynput
# - ON Windows:
#   - pip install pywin32
# - ON Posix/Linux:
#   - pip install evdev
#
import threading
from pynput import keyboard, mouse
import time
import os
import subprocess
import sys
import yaml
import hashlib
import ctypes
import webview
if os.name == 'nt':
    import win32con
    import win32api
#if os.uname().sysname == "Linux":    
if os.name == 'posix':
    from evdev import UInput, ecodes as e
#if os.uname().sysname == "Darwin":
#    pass

config_file_name = 'config-url-monitor-saver.yml'
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

config_file_path = os.path.join(application_path, config_file_name)

# tick in milli seconds, multiple of 30. Used in making Frame animation smooth.
tick=30
rtick=tick/1000

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
            #print(f"config data = {config['screens']}")
        except yaml.YAMLError as exc:
            print(exc)
except:
    print(f"Config file not found at location: {config_file_path}")
    sys.exit(1)

# Function to get the dictionary with the given 'id'
def get_dict_by_id(data, n):
    return next((item for item in data if item["id"] == n), None)

print(f"Webview screens = {webview.screens}")
for s in webview.screens:
    print(f"Webview frames = {s.frame}")
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
speed_x = config['speed_x']
speed_y = config['speed_y']
screens = []
screens.append( { 'id' : 0, 'X': 0, 'Y': 0, 'Width': 1920, 'Height': 1032 } )
if config['screens']:
    screens = config['screens']
print(f"screens = {screens}")
cScreen = get_dict_by_id(screens, 0)   # Current Screen, default is None, for the Default screen.
cScreen_changed = True

#Frame starting position
winx = cScreen['X']
winy = cScreen['Y']

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
        if os.name == 'nt':
            ctypes.windll.user32.SendMessageW(65535, 274, 61808, 2)
        else:
            subprocess.run(["xset", "-display", ":0.0", "dpms", "force", "off"])
def screenOn():
    if screenoff_enabled:
        if os.name == 'nt':
            ctypes.windll.user32.SendMessageW(65535, 274, 61808, -1)
            moveCursor()
        else:
            subprocess.run(["xset", "dpms", "force", "on"])
            time.sleep(1)
            # Simulate key press
            with UInput() as ui:
                ui.write(e.EV_KEY, e.KEY_ESCAPE, 1)  # Key down
                ui.write(e.EV_KEY, e.KEY_ESCAPE, 0)  # Key up
                ui.syn()            

def moveCursor():
    if os.name == 'nt':
        x, y = (0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y)

# Generate the URL with Authentication for Display
authenticated_url = base_url+generate_auth_hash(False)

# Event to control the main loop and listeners
terminate_event = threading.Event()

def destroy(window, timeInSec):
    global speed_x, speed_y, winx, winy, rtick, tick, cScreen, screens, cScreen_changed
    cScreen_changed = True
    # top=None
    # bottom=None
    # right=None
    # left=None
    for _ in range(timeInSec*tick):
        time.sleep(rtick)
        if terminate_event.is_set():
            break           
        if cScreen_changed:
            cScreen_changed=False
            top=None
            bottom=None
            right=None
            left=None
            for p in cScreen['placements']:
                if p['position'] == 'Top':
                    top=p['neighbour']
                if p['position'] == 'Bottom':
                    bottom=p['neighbour']
                if p['position'] == 'Left':
                    left=p['neighbour']
                if p['position'] == 'Right':
                    right=p['neighbour']                         
        if winx < cScreen['X']:
            if left==None:
                speed_x = speed_x * -1
            else:
                cScreen = get_dict_by_id(screens, left)
                cScreen_changed = True
                break
        if winx + frame_width > cScreen['Width']:
            if right==None:
                speed_x = speed_x * -1
            else:
                cScreen = get_dict_by_id(screens, right)
                cScreen_changed = True
                break
        if winy < cScreen['Y']:
            if top==None:
                speed_y = speed_y * -1
            else:
                cScreen = get_dict_by_id(screens, top)
                cScreen_changed = True
                break
        if winy + frame_height > cScreen['Height']:
            if bottom==None:
                speed_y = speed_y * -1
            else:
                cScreen = get_dict_by_id(screens, bottom)
                cScreen_changed = True
                break
        nx = winx + speed_x * rtick
        ny = winy + speed_y * rtick
        winx = int(nx)
        winy = int(ny)
        window.move(winx, winy)  
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

try:
    if __name__ == "__main__":
        # Create and start the keypress and mouse listener threads
        keyboard_listenerO = keyboard.Listener(on_press=on_key_event)
        mouse_listenerO = mouse.Listener(on_move=on_mouse_event)
        keyboard_thread = threading.Thread(target=keyboard_listenerO.start)
        mouse_thread = threading.Thread(target=mouse_listenerO.start)
        keyboard_thread.start()
        mouse_thread.start()

        # Main program code
        while not terminate_event.is_set():
            if cScreen_changed:                
                print(f"cScreen = {cScreen}")
                print(f"webview screen = {webview.screens[cScreen['id']]}")
            screenOn()
            mywin = webview.create_window('ZoneMinder', authenticated_url, x=winx, y=winy, 
                                        width=frame_width, height=frame_height,
                                        screen=webview.screens[cScreen['id']],
                                        frameless=True, draggable=True)
            webview.start(destroy, (mywin, seconds_on))
            if terminate_event.is_set():
                screenOn()
                break
            
            screenOff()
            for _ in range(seconds_off*tick):
                if terminate_event.is_set():
                    screenOn()
                    break
                time.sleep(rtick)    

        # Stop the listeners if the program is terminating
        keyboard_listenerO.stop()
        mouse_listenerO.stop()

        # Wait for the threads to finish
        keyboard_thread.join()
        mouse_thread.join()
        # if adding threads, then join them here.

        # end.
except Exception as e:
    print(f"Error: {e}")
    print(sys.exc_info()[0])
    sys.exit(1)
else:
    sys.exit(0)