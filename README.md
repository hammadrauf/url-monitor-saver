# Url-monitor-saver
Monitors a URL in python Browser and Act As a Screen saver turning off monitor frequently
and turning back on again. The URL and intervals for Screen-ON and Screen-Off are to be
given in as YAML text config file. This YAML file should be in the same folder as the executable
file.
  
ZoneMinder article: [https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/](https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/)
  
screen_Off function is only for Windows based computers.

## Author
Hammad Rauf (rauf.hammad@gmail.com)

## Article
Article about this monitor-saver: [https://andromedabay.ddns.net/zoneminder-screen-saver/](https://andromedabay.ddns.net/zoneminder-screen-saver/)
## License
MIT (Open Source, Free)

## Sample Config (YAML) file contents
```
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
```

## Config file name and location
There should a text file named "config-url-monitor-saver.yml" in the folder the python, executable, or .scr file is installed/saved. The
contents of this Yaml file can be like the one shown in sample above.

## Config file - Explanation
This is a Yaml file. YAML is a simple text based file, which uses indentation, '-', and arbitrary names to describe data configuration
properties. A quick tutorial on YAML syntax is [here](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started).
  
Following is an explanation of each field:
* domain: The Zoneminder website Domain Name. 
* secret_key: The Secret key used in Zoneminder -\> Options -\> System -\> AUTH_HASH_SECRET
* username: A Zoneminder user name, created specifically for this screen saver
* password_hash: Password Hash of the above username, as extracted from Zoneminder Database (MySql) table 'Users'. More information on
this at this [page](https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/#finding-the-password-hash).
  ```
  mysql> use zm;
  mysql> select Username,Password from zm.Users where Username = '\<\<USERNAME\>\>';
  ```
* seconds_off: Time in seconds, the Window (or Window and Screen) remain OFF.
* seconds_on: Time in seconds, the Window (or Window and Screen) remain ON.
* frame_width: Window Width in pixels.
* frame_height: Window Height in pixels.
* screenoff_enabled: True or False. Specifies if Screen or Monitor is to be turned OFF or not. If it is false, then only the
Window will be hidden during "seconds_off" time period. This option does not work as expected when using .scr file, only works when
using .exe or .py file.
* speed_x: Integer. Speed of Window movement in X-Axis. Standard value is 3.
* speed_y: Integer. Speed of Window movement in Y-Axis. Standard value is 3.
* screens: Optional. A YAML List. Specifies the number of Physical monitors used in your system.

## Pre-requisites
Python3 should be installed. Then you will also need to install the following using pip:
- pip install pyyaml, pywin32
- pip install pywebview, pynput
Zoneminder settings should be set as described in this site:
- [https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/#configuring-zoneminder-to-allow-logins-via-authentication-hash](https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/#configuring-zoneminder-to-allow-logins-via-authentication-hash)

## Use PyInstaller to Make EXE
PyInstaller Link: [https://pyinstaller.org/en/stable/operating-mode.html](https://pyinstaller.org/en/stable/operating-mode.html)
```
pip install pyinstaller
pyinstaller --onefile --windowed url-monitor-saver.py
```

## Convert to Screen Saver
Rename the .exe file to .scr. Then right click on it and Install. Some Specific Windows behavior like screen saver settings is not implemented.

## Screen Saver Video
[![Watch the video](https://img.youtube.com/vi/0OwXKH7XfvY/hqdefault.jpg)](https://www.youtube.com/watch?v=0OwXKH7XfvY)
