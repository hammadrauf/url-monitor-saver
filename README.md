# Url-monitor-saver
Monitors a URL in python Browser and Act As a Screen saver turning off monitor frequently
and turning back on again. The URL and intervals for Screen-ON and Screen-Off are to be
given in as YAML text config file. This YAML file should be in the same folder as the executable
file.
  
Works with any URL or ZomeMinder URL with Authentication Hash.
  
ZoneMinder article: [https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/](https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/)
  
screen_Off function is only for Windows based computers.

## Author
Hammad Rauf, :canada:, :pakistan:

## Code Re-used Attribution
* This software borrows some lines of code related to hiding system mouse pointer under Windows operating system from:  
  - [Pete Richards - windows-cursor-hiding-utility](https://github.com/PRich57/windows-cursor-hiding-utility)
  Its license text (MIT License) is copied in the [License file](./LICENSE).
* Thanks to Microsoft Copilot (ChatGPT), for some code structures and for reducing my coding time significantly.

## Article
Article about this monitor-saver: [https://andromedabay.ddns.net/zoneminder-screen-saver/](https://andromedabay.ddns.net/zoneminder-screen-saver/)
## License
MIT (Open Source, Free)

## Sample Config (YAML) file contents
```
# Configuration Items are explained in README.md below.
---
  domain: "zoneminder.xyz.com"
  secret_key: "SomeRandomSecretKey-FromZoneMinder-Options"
  username: "SomeUserName"
  password_hash: "PasswordHash-From-MySQLDB-table-zoneminder"
  password: "Some-optional-password-for-ZM"
  use_zoneminder_domain: False
  o_url: "https://www.earthcam.com/world/canada/toronto/cntower/?cam=cntower2"
  o_username: "user01-optional"
  o_password: "strong_password-optional"
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
* domain: The private Zoneminder website Domain Name. For ordinary URLs use (use_zoneminder_domain: False, and o_url='https://xyz.com')
* secret_key: The Secret key used in Zoneminder -\> Options -\> System -\> AUTH_HASH_SECRET
* username: A Zoneminder user name, created specifically for this screen saver
* password_hash: Password Hash of the above username, as extracted from Zoneminder Database (MySql) table 'Users'. More information on
this at this [page](https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/#finding-the-password-hash).
  ```
  mysql> use zm;
  mysql> select Username,Password from zm.Users where Username = '\<\<USERNAME\>\>';
  ```
* password: Optional password for use with ZoneMinder-Username in Basic Authentication Mode. It over-rides the password_hash if provided.
* use_zoneminder_domain: True or False. Specifies if private Zoneminder fields are to be used or o_url should be used. 
* o_url:  A custom URL string to be shown in the screen saver if 'use_zoneminder_domain' is False.
* o_username: Optional username for use with o_url
* o_password: Optional password for use with o_url
* seconds_off: Time in seconds, the Window (or Window and Screen) remain OFF.
* seconds_on: Time in seconds, the Window (or Window and Screen) remain ON.
* frame_width: Window Width in pixels.
* frame_height: Window Height in pixels.
* screenoff_enabled: True or False. Specifies if Screen or Monitor is to be turned OFF or not. If it is false, then only the
Window will be hidden during "seconds_off" time period. This option does not work as expected when using .scr file, only works when
using .exe or .py file.
* speed_x: Integer. Speed of Window movement in X-Axis. Standard value is 3.
* speed_y: Integer. Speed of Window movement in Y-Axis. Standard value is 3.
* use_one_screen: True or False. On a multiscreen computer system, specifiy if only 1 screen should show the Screen Saver Window.
* start_screen_id: Integer from 0 to N-1, where N is the number of Monitors in your computer system. Screen saver window will appear on this Monitor id. The Screen Id refers to Ids in 'screens' YAML structure.
* screens: Optional. A YAML List. Specifies the number of Physical monitors used in your system, along with their dimensions in Pixels. Please see the sample/shadow config file and customize it according to your setup. More on this in next section.

### Screens - Configuraion
![Image 3 Monitor Setup Example](https://github.com/hammadrauf/url-monitor-saver/blob/main/images/Test_Setup_-_Screens_and_Relative_sizes.png?raw=true)
In the above Image 3 monitor setup is shown that was used in Testing this software. The corresponding "screens" YAML config is shown below.
```
.... << Other Configuration - Redacted >>
  screens:
    - id: 0
      X: 0
      Y: 0
      Width: 1920
      Height: 1080
      placements:
        - neighbour: 1
          position: "Left"
        - neighbour: 2
          position: "Bottom"
    - id: 1
      X: -1920
      Y: 0
      Width: 1920
      Height: 1080    
      placements:
        - neighbour: 0
          position: "Right"
    - id: 2
      X: 0
      Y: 1080
      Width: 1440
      Height: 900    
      placements:
        - neighbour: 0
          position: "Top"
```

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
