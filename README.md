# honeydew
A basic SSH honeypot to capture IP Adresses, usernames, passwords, and commands.

## Usage

SSH_HONEYPY requires a bind IP address (`-a`) and network port to listen on (`-p`). Use `0.0.0.0` to listen on all network interfaces. 

```
-a / --address: Bind address. (Default : 0.0.0.0)
-p / --port: Port. (Default: 8022)
-c / --concurrent_connections: Amount of allowed concurrent connections. (Default: 100)
-b / --banner: Flag to enable delayed SSH sessions. (Default: False)
-d / --delay: Amount of delay in seconds (Default: 5)
```

Example: `python3 main.py -a 127.0.0.1 -p 8022`

**Optional Arguments**

A username (`-u`) and password (`-w`) can be specified to authenticate the SSH server. The default configuration will accept all usernames and passwords.

```
-u / --username: Username.
-w / --password: Password.
```

Example: `python3 main.py -a 0.0.0.0 -p 22 -u root -w root`

# TODO:
**Overview/Monitorings**
- [X] Add overview of amount of connections by IP
- [ ] ~~Add overview of amount of commands by IP~~
- [X] Add overview of username attempt count
- [X] Add overview of commands by session
- [X] Add a storage method to save this data
- [X] Add a basic web interface for the required information. 

**Script**
- [ ] Check if script methods can be put in modulair instances. 
- [x] Support command history in current session
- [x] Add basic sys variable support, dynamically. ( just like commands )
- [x] Add support for only specifying a specific password. ( Support any username that gives the password )
- [ ] Support multiple usernames (in validation)
- [ ] Support multiple passwords (in validation)
- [ ] Add a correct way to stop the webserver thread
- [ ] Check command logging, it still receives \r 

**Usage**
- [x] Allow change of motd banner
- [x] Allow change of hostname
- [x] Allow change of log directory 
- [ ] Create a systemd setup script
- [ ] Create a docker container to run the application
  
