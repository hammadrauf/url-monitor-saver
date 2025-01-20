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
  seconds_off: 5
  seconds_on: 8
  frame_width: 1024
  frame_height: 1000
  screenoff_enabled: False
  speed_x: 90
  speed_y: 60
```
## Config file name and location
There should a text file named "config-url-monitor-saver.yml" in the folder the python, executable, or .scr file is installed/saved. The contents of this Yaml file can be like the one shown in sampkle above.
  
## Pre-requisites
Python3 should be installed. Then you will also need to install the following using pip:
- pip install pyyaml, pywin32
- pip install pywebview, pynput

## Use PyInstaller to Make EXE
PyInstaller Link: [https://pyinstaller.org/en/stable/operating-mode.html](https://pyinstaller.org/en/stable/operating-mode.html)
```
pip install pyinstaller
pyintaller --onefile --windowed url-monitor-saver.py
```

## Convert to Screen Saver
Rename the .exe file to .scr. Then right click on it and Install. Some Specific Windows behavior like screen saver settings is not implemented.
