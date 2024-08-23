import paramiko
import threading
from datetime import datetime, timedelta
from honeypot.logger import creds_logger, funnel_logger, server_logger
import os
import json
import random
# Define the class that will handle the SSH server.
class Server(paramiko.ServerInterface):
    # Define the constructor for the Server class.
    def __init__(self, client_ip: str, input_username:str|None=None, input_password:str|None=None, hostname:str="honeydew", env_directory:str=""):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.client_user = None
        self.input_username = input_username
        self.input_password = input_password
        self.hostname = hostname
        self.connected_time = datetime.now()
        self.env_directory = env_directory
        self.json_env_username = "client_logins.json"
        self.start_time = datetime.now()
        self.random_server_start_timem = self.__get_random_date(datetime(self.start_time.year, 1, 10), self.start_time)
        self.login_command = None
        self.logins_directory = os.path.join(self.env_directory, "logins")
        self.json_path = os.path.join(self.logins_directory, self.json_env_username)
        os.makedirs(self.logins_directory, exist_ok=True)
        try:
            server_logger.info("Loading server key.")
            self.host_key = paramiko.RSAKey(filename="server.key")
            server_logger.info("Server key loaded.")
        except FileNotFoundError:
            server_logger.info("Creating server key.")
            self.host_key = paramiko.RSAKey.generate(2048)
            self.host_key.write_private_key_file("server.key")
            server_logger.info("Server key created.")
        
        self.__prompt = f"{self.hostname}$ "
        
        # Define the prompt for the SSH server.

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            server_logger.info(f'Client {self.client_ip} requested a session on channel {chanid}.')
            return paramiko.OPEN_SUCCEEDED
        
    def get_allowed_auths(self, username: str):
        return "password"
    
    def check_auth_password(self, username: str, password: str):
        creds_logger.info(f'Client {self.client_ip} attempted connection with ' + f'username: {username}, ' + f'password: {password}')
        self.client_user = username
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                creds_logger.info(f'Client {self.client_ip} successfully logged in with, {username}, {password}')
                server_logger.info(f'Client {self.client_ip} successfully established a connection.')
                self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=True)
                return paramiko.AUTH_SUCCESSFUL
            else:
                creds_logger.info(f'Client {self.client_ip} failed to login with, {username}, {password}')
                server_logger.info(f'Client {self.client_ip} failed to established a connection.')
                self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=False)
                return paramiko.AUTH_FAILED
        elif self.input_username is not None:
            if username == self.input_username:
                creds_logger.info(f'Client {self.client_ip} successfully connected with, {username}, {password}')
                server_logger.info(f'Client {self.client_ip} successfully established a connection.')
                self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=True)
                return paramiko.AUTH_SUCCESSFUL
            else:
                creds_logger.info(f'Client {self.client_ip} failed to login with, {username}, {password}')
                server_logger.info(f'Client {self.client_ip} failed to established a connection.')
                self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=False)
                return paramiko.AUTH_FAILED
        elif self.input_password is not None: 
            if password == self.input_password:
                creds_logger.info(f'Client {self.client_ip} successfully connected with, {username}, {password}')
                server_logger.info(f'Client {self.client_ip} successfully established a connection.')
                self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=True)
                return paramiko.AUTH_SUCCESSFUL
            else:
                creds_logger.info(f'Client {self.client_ip} failed to login with, {username}, {password}')
                server_logger.info(f'Client {self.client_ip} failed to established a connection.')
                self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=False)
                return paramiko.AUTH_FAILED
        else:
            creds_logger.info(f'Client {self.client_ip} successfully connected with, {username}, {password}')
            server_logger.info(f'Client {self.client_ip} successfully established a connection.')
            self.add_login(client_ip=self.client_ip, client_username=username, client_password=password, successfull=True)
            return paramiko.AUTH_SUCCESSFUL
        
    def check_channel_shell_request(self, channel: paramiko.Channel):
        server_logger.info(f'Session {self.client_user}@{self.client_ip} requested a shell.')
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def prompt(self):
        if self.client_user is not None:
            self.__prompt = f"{self.client_user}@{self.hostname}$ "
        else:
            self.__prompt = f"{self.hostname}$ "
        return self.__prompt
    
    def check_channel_exec_request(self, channel: paramiko.Channel, command: bytes):
        command = str(command)
        # if a command is entered by the client, log it
        if command:
            self.login_command = command
            funnel_logger.info(f'Session {self.client_user}@{self.client_ip} parsed the following command while connecting: {command}')
            date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            command_history_directory = f"{self.env_directory}/command_history"
            os.makedirs(command_history_directory, exist_ok=True)
            command_history_file = f"{command_history_directory}/command_history-{self.client_ip}-{date}.json"
            json.dump([{"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"command": command}], open(command_history_file, "w"))
            return False
        return True
        
    def add_login(self, client_ip, client_username, client_password, successfull):
        self.__add_username(client_username=client_username)
        self.__update_daily_login_log(client_ip=client_ip, client_username=client_username, client_password=client_password, successfull=successfull)
        self.__update_weekly_log(client_ip=client_ip, client_username=client_username, client_password=client_password, successfull=successfull)
        self.__update_monthly_log(client_ip=client_ip, client_username=client_username, client_password=client_password, successfull=successfull)
    
    def __add_username(self, client_username):
        # Check if self.env_directory exists and create it if not
        if not os.path.exists(self.env_directory):
            os.makedirs(self.env_directory, exist_ok=True)
            server_logger.info(f"Created directory: {self.env_directory}")   
        
        # Check if the JSON file exists, create a new one with initial data if not
        if not os.path.exists(self.json_path):
            clients = {
                client_username: 1
            }
            server_logger.info(f"Created new clients file with initial username: {client_username}")
        else:
            # Load existing client data from JSON file
            with open(self.json_path, 'r') as json_file:
                clients = json.load(json_file)
            
            # Check if the client_ip already exists, and update the connection count
            if client_username in clients:
                clients[client_username] += 1
                server_logger.info(f"Updated connection count for username: {client_username}")
            else:
                clients[client_username] = 1
                server_logger.info(f"Added new username: {client_username}")

        # Write updated client data back to the JSON file
        with open(self.json_path, 'w') as json_file:
            json.dump(clients, json_file, indent=4)
            server_logger.info(f"Saved updated username data to {self.json_path}")
    
    def __update_daily_login_log(self, client_ip, client_username, client_password, successfull):
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(self.logins_directory, exist_ok=True)
        daily_log_filename = os.path.join(self.logins_directory, f"logins_{current_date}.json")

        # Check if the daily log file exists, create it if not
        if not os.path.exists(daily_log_filename):
            daily_log = []
            server_logger.info(f"Created new daily log file: {daily_log_filename}")
        else:
            # Load existing daily log data from JSON file
            with open(daily_log_filename, 'r') as json_file:
                daily_log = json.load(json_file)

        # Add new connection entry with timestamp
        connection_entry = {
            "ip": client_ip,
            "username": client_username,
            "password": client_password,
            "successfull_login": successfull,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        daily_log.append(connection_entry)

        # Write updated daily log data back to the JSON file
        with open(daily_log_filename, 'w') as json_file:
            json.dump(daily_log, json_file, indent=4)
            server_logger.info(f"Updated daily log file: {daily_log_filename}")
            
    def __update_weekly_log(self, client_ip, client_username, client_password,successfull):
        # Get the start of the current week (Monday)
        current_date = datetime.now()
        os.makedirs(self.logins_directory, exist_ok=True)
        start_of_week = (current_date - timedelta(days=current_date.weekday())).strftime("%Y-%m-%d")
        weekly_log_filename = os.path.join(self.logins_directory, f"logins_week_{start_of_week}.json")

        # Check if the weekly log file exists, create it if not
        if not os.path.exists(weekly_log_filename):
            weekly_log = []
            server_logger.info(f"Created new weekly log file: {weekly_log_filename}")
        else:
            # Load existing weekly log data from JSON file
            with open(weekly_log_filename, 'r') as json_file:
                weekly_log = json.load(json_file)

        # Add new connection entry with timestamp
        connection_entry = {
            "ip": client_ip,
            "username": client_username,
            "password": client_password,
            "successfull_login": successfull,
            "timestamp": current_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        weekly_log.append(connection_entry)

        # Write updated weekly log data back to the JSON file
        with open(weekly_log_filename, 'w') as json_file:
            json.dump(weekly_log, json_file, indent=4)
            server_logger.info(f"Updated weekly log file: {weekly_log_filename}")

    def __get_random_date(self, start_date, end_date):
        """
        Generate a random date between `start_date` and `end_date`.
        
        :param start_date: A datetime object representing the start of the range.
        :param end_date: A datetime object representing the end of the range.
        :return: A datetime object representing the random date.
        """
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        random_date = start_date + timedelta(days=random_days)
        return random_date


    def __update_monthly_log(self, client_ip, client_username, client_password, successfull):
        # Get the current date and month
        current_date = datetime.now()
        month = current_date.strftime("%Y-%m")
        os.makedirs(self.logins_directory, exist_ok=True)
        monthly_log_filename = os.path.join(self.logins_directory, f"logins_{month}.json")

        # Check if the monthly log file exists, create it if not
        if not os.path.exists(monthly_log_filename):
            monthly_log = []
            server_logger.info(f"Created new monthly log file: {monthly_log_filename}")
        else:
            # Load existing monthly log data from JSON file
            with open(monthly_log_filename, 'r') as json_file:
                monthly_log = json.load(json_file)

        # Add new connection entry with timestamp
        connection_entry = {
            "ip": client_ip,
            "username": client_username,
            "password": client_password,
            "successfull_login": successfull,
            "timestamp": current_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        monthly_log.append(connection_entry)

        # Write updated monthly log data back to the JSON file
        with open(monthly_log_filename, 'w') as json_file:
            json.dump(monthly_log, json_file, indent=4)
            server_logger.info(f"Updated monthly log file: {monthly_log_filename}")