class HoneypotSettings:
    def __init__(self, address:str="0.0.0.0", port:int=8022, username:str|None|list=None, password:str|None|list=None, concurrent_connections:int=100, banner:bool=True, delay:int=5, overwrite_arguments:bool=False, hostname:str="honeydew", log_directory:str="./logs", env_directory="./env", banner_message="Welcome to the SSH session\r\n\r\n", webserver_enabled:bool=False, webserver_port:int=5000, webserver_address:str="127.0.0.1"):
        """ Configuration settings for the honeypot server. """
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.concurrent_connections = concurrent_connections
        self.banner = banner
        self.delay = delay
        self.hostname = hostname
        self.overwrite_arguments = overwrite_arguments
        self.log_directory = log_directory
        self.env_directory = env_directory
        self.banner_message = banner_message    
        self.webserver_enabled = webserver_enabled
        self.webserver_port = webserver_port
        self.webserver_address = webserver_address
    
    