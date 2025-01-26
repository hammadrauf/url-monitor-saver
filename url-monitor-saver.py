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
import logging

if os.name == 'nt':
    import win32con
    import win32api
    from ctypes import wintypes
    # Constants
    OCR_NORMAL = 32512
    SPI_SETCURSORS = 0x0057
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    # Load required DLLs
    user32 = ctypes.windll.user32    
    # Function prototypes
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    user32.SetSystemCursor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    user32.SetSystemCursor.restype = ctypes.c_bool
    user32.CopyIcon.argtypes = [ctypes.c_void_p]
    user32.CopyIcon.restype = ctypes.c_void_p
    user32.LoadCursorW.argtypes = [ctypes.c_void_p, ctypes.c_int]
    user32.LoadCursorW.restype = ctypes.c_void_p
    user32.SystemParametersInfoW.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    user32.SystemParametersInfoW.restype = ctypes.c_bool

#if os.uname().sysname == "Linux":    
if os.name == 'posix':
    from evdev import UInput, ecodes as e
    from ctypes.util import find_library
    x11 = None
    xfixes = None
    d = None
    if 'WAYLAND_DISPLAY' in os.environ:
        wayland = True
    else:
        x11 = ctypes.cdll.LoadLibrary(find_library('X11'))
        xfixes = ctypes.cdll.LoadLibrary(find_library('Xfixes'))
        d = x11.XOpenDisplay(None)
        wayland = False    

# if os.uname().sysname == "Darwin":
#    pass

logging.basicConfig(level=logging.INFO)
logging.debug('url-monitor-saver screen saver - Logger started!')
logger = logging.getLogger(__name__)

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
  use_zoneminder_domain: False
  o_url: "https://www.earthcam.com/world/canada/toronto/cntower/?cam=cntower2"  
  seconds_off: 23
  seconds_on: 120
  frame_width: 850
  frame_height: 850
  screenoff_enabled: False
  speed_x: 3
  speed_y: 3
  use_one_screen: False
  start_screen_id: 0
  screens:
    - id: 0
      X: 0
      Y: 0
      Width: 1920
      Height: 1080
      placements:
        - neighbour: 1
          position: "Left"
    - id: 1
      X: -1920
      Y: 0
      Width: 1920
      Height: 1080    
      placements:
        - neighbour: 0
          position: "Right"
'''

config={}
try:   
    with open(config_file_path) as stream:
        try:
            config=yaml.safe_load(stream)
            #print(f"config data = {config['screens']}")
        except yaml.YAMLError as exc:
            #print(exc)
            logger.error(exc)
except:
    #print(f"Config file not found at location: {config_file_path}")
    logger.error(f"Config file not found at location: {config_file_path}")
    sys.exit(1)

# Function to get the dictionary with the given 'id'
def get_dict_by_id(data, n):
    return next((item for item in data if item["id"] == n), None)

logger.debug(f"Webview screens = {webview.screens}")
for s in webview.screens:
    logger.debug(f"Webview frames = {s.frame}")
domain=config['domain']
#base_url = f"https://{domain}/index.php?view=watch&mid=1&auth="
base_url=f"https://{domain}/index.php?view=montage&group=1&scale=0.5&auth="
secret_key = config['secret_key']
username = config['username']
password_hash = config['password_hash']
use_zoneminder_domain = config['use_zoneminder_domain']
o_url = config['o_url']
seconds_off = config['seconds_off']
seconds_on = config['seconds_on']
frame_width = config['frame_width']
frame_height = config['frame_height']
screenoff_enabled = config['screenoff_enabled']
speed_x = config['speed_x']
speed_y = config['speed_y']
start_screen_id = config['start_screen_id']
use_one_screen = config['use_one_screen']
screens = []
screens.append( { 'id' : 0, 'X': 0, 'Y': 0, 'Width': 1920, 'Height': 1032 } )
if config['screens']:
    screens = config['screens']
logger.debug(f"screens = {screens}")
cScreen = get_dict_by_id(screens, start_screen_id)   # Current Screen, default is None, for the Default screen.
cScreen_changed = True

#Frame starting position
winx = cScreen['X']
winy = cScreen['Y']

authenticated_url = None

# Event to control the main loop and listeners
terminate_event = threading.Event()


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


def destroy(window, timeInSec):
    global speed_x, speed_y, winx, winy, rtick, tick, cScreen, screens, cScreen_changed
    cScreen_changed = True
    top=None
    bottom=None
    right=None
    left=None
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
            if not use_one_screen:
                for p in cScreen['placements']:
                    if p['position'] == 'Top':
                        top=p['neighbour']
                    if p['position'] == 'Bottom':
                        bottom=p['neighbour']
                    if p['position'] == 'Left':
                        left=p['neighbour']
                    if p['position'] == 'Right':
                        right=p['neighbour']                         
        if winx + speed_x < cScreen['X']:
            if left==None or use_one_screen: 
                speed_x = speed_x * -1
            else:
                if winx + speed_x + frame_width < cScreen['X']:
                    nextScreen = get_dict_by_id(screens, left)
                    if winx + speed_x + frame_height + speed_y > nextScreen['Y']:
                        speed_y = speed_y * -1
                    else:
                        cScreen = get_dict_by_id(screens, left)
                        cScreen_changed = True
                        break
        if winx + speed_x + frame_width > cScreen['X']+cScreen['Width']:
            if right==None or use_one_screen:
                speed_x = speed_x * -1
            else:
                if winx + speed_x > cScreen['X']+cScreen['Width']:
                    cScreen = get_dict_by_id(screens, right)
                    cScreen_changed = True
                    break
        if winy + speed_y < cScreen['Y']:
            if top==None or use_one_screen:
                speed_y = speed_y * -1
            else:
                if winy + speed_y + frame_height < cScreen['Y']:
                    cScreen = get_dict_by_id(screens, top)
                    cScreen_changed = True
                    break
        if winy + speed_y + frame_height > cScreen['Y']+cScreen['Height']:
            if bottom==None or use_one_screen:
                speed_y = speed_y * -1
            else:
                if winy + speed_y > cScreen['Y']+cScreen['Height']:
                    cScreen = get_dict_by_id(screens, bottom)
                    cScreen_changed = True
                    break
        nx = winx + speed_x
        ny = winy + speed_y
        winx = nx
        winy = ny
        if use_one_screen:
            if winx < cScreen['X'] or winy < cScreen['Y'] or winx > cScreen['X']+cScreen['Width'] or winy > cScreen['Y']+cScreen['Height']:
                logger.debug(f'\n===> winx = {winx}, winy = {winy}. nx = {nx}, ny = {ny}, speed_x = {speed_x}, speed_y = {speed_y}')
                logger.debug(f'   > lower-right("{winx+frame_width-1}","{winy+frame_height-1}")')
            else:
                logger.debug('.',end='')
        window.move(winx, winy)  
    window.destroy()

def on_key_event(key):
    terminate_event.set()
    show_pointer()  # Show pointer when screen saver is terminated
    return False

def on_mouse_event(x, y):
    terminate_event.set()
    show_pointer()  # Show pointer when screen saver is terminated
    return False

def keypress_listener():
    with keyboard.Listener(on_press=on_key_event) as listener:
        listener.join()

def mouse_listener():
    with mouse.Listener(on_move=on_mouse_event) as listener:
        listener.join()

def create_invisible_cursor() -> ctypes.c_void_p:
    #cursor = None
    if os.name=='nt':
        # Create a blank cursor using ctypes
        # ANDmask = ctypes.c_char_p(b'\x00' * 8)
        # XORmask = ctypes.c_char_p(b'\x00' * 8)
        # cursor = ctypes.windll.user32.CreateCursor(None, 0, 0, 8, 8, ANDmask, XORmask)
        and_mask = (ctypes.c_ubyte * 4)(0xFF, 0xFF, 0xFF, 0xFF)
        xor_mask = (ctypes.c_ubyte * 4)(0, 0, 0, 0)
        cursor = user32.CreateCursor(None, 0, 0, 1, 1, and_mask, xor_mask)        
    if os.name == 'posix':
        black = ctypes.c_ulong(0)
        pixmap = x11.XCreatePixmap(d, x11.XDefaultRootWindow(d), 1, 1, 1)
        gc = x11.XCreateGC(d, pixmap, 0, None)
        x11.XSetForeground(d, gc, black)
        x11.XFillRectangle(d, pixmap, gc, 0, 0, 1, 1)
        cursor = x11.XCreatePixmapCursor(d, pixmap, pixmap, ctypes.pointer(black), ctypes.pointer(black), 0, 0)
        x11.XFreePixmap(d, pixmap)
        x11.XFreeGC(d, gc)
    return cursor

original_cusor = None
invisible_cursor = create_invisible_cursor()

def hide_pointer() -> None:
    global original_cursor
    if os.name == 'nt':
        #ctypes.windll.user32.SetCursor(invisible_cursor)
        original_cursor = user32.CopyIcon(user32.LoadCursorW(None, OCR_NORMAL))
        if user32.SetSystemCursor(invisible_cursor, OCR_NORMAL):
            logger.debug("Cursor hidden")
        else:
            logger.debug("Failed to hide cursor")        
    else:
        if wayland:
            print("Wayland detected. Hide System Mouse Pointer - custom handling needed. Not implemented in screen saver.")
        else:
            x11.XDefineCursor(d, x11.XDefaultRootWindow(d), invisible_cursor)
            x11.XFlush(d)

def show_pointer() -> None:
    global original_cursor
    if os.name == 'nt':
        #ctypes.windll.user32.SetCursor(ctypes.windll.user32.LoadCursorW(None, win32con.IDC_ARROW))
        if original_cursor:
            if user32.SetSystemCursor(original_cursor, OCR_NORMAL):
                logger.debug("Cursor restored")
                # Force a cursor update across all monitors
                user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            else:
                logger.debug("Failed to restore cursor")
        else:
            logger.debug("No original cursor to restore")        
    else:
        if wayland:
            print("Wayland detected. Show System Mouse Pointer - custom handling needed. Not implemented in screen saver")
        else:
            x11.XUndefineCursor(d, x11.XDefaultRootWindow(d))
            x11.XFlush(d)

try:
    if __name__ == "__main__":
        #root = tk.Tk()
        # Create and start the keypress and mouse listener threads
        keyboard_listenerO = keyboard.Listener(on_press=on_key_event)
        mouse_listenerO = mouse.Listener(on_move=on_mouse_event)
        keyboard_thread = threading.Thread(target=keyboard_listenerO.start)
        mouse_thread = threading.Thread(target=mouse_listenerO.start)
        keyboard_thread.start()
        mouse_thread.start()

        # Main program code
        while not terminate_event.is_set():

            # Generate the URL with Authentication for Display
            #   This is inside a loop because Zoneminer Auth Hash expires by default after 2 hours. This way it gets regenerated.
            if use_zoneminder_domain:
                authenticated_url = base_url+generate_auth_hash(False)
            else:
                authenticated_url = o_url

            if cScreen_changed:                
                logger.debug(f"cScreen = {cScreen}")
                logger.debug(f"webview screen = {webview.screens[cScreen['id']]}")
            screenOn()
            mywin = webview.create_window('URL Monitor Saver', authenticated_url, x=winx, y=winy, 
                                        width=frame_width, height=frame_height,
                                        screen=webview.screens[cScreen['id']],
                                        frameless=True, draggable=False)
            hide_pointer()  # Hide mouse-pointer when screen saver is active
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
    logger.error(f"Error: {e}")
    logger.error(sys.exc_info()[0])
    sys.exit(1)
else:
    sys.exit(0)