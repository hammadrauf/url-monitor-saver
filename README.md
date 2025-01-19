# Url-monitor-saver
Monitors a URL in Default Browser and Act As a Screen saver turning off monitor frequently
and turning back on again. The URL and intervals for Screen-ON and Screen-Off are to be
given in as YAML text config file. This YAML file should be in the same folder as the executable
file.
  
ZoneMinder article: [https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/](https://techbit.ca/2018/11/logging-into-zoneminder-using-an-authentication-hash/)
  
screen_Off function is only for Windows based computers.

## Author
Hammad Rauf (rauf.hammad@gmail.com)

## License
MIT (Open Source, Free)

## Sample YAML file contents
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
```
