import socket
import threading
import time
from ssh.handlers import client_handle 
from honeypot.logger import funnel_logger, server_logger
from honeypot.objects import HoneypotSettings
import os
import json
from datetime import datetime, timedelta
from honeypot.webserver import app

class HoneypotServer:
    def __init__(self, settings: HoneypotSettings| None = None):
        self.address = settings.address
        self.port = settings.port
        self.username = settings.username
        self.password = settings.password
        self.hostname = settings.hostname
        self.concurrent_connections = settings.concurrent_connections
        self.server_socket = None
        self.client_threads = []
        self.client_sockets = []
        self.running = True
        self.banner_enabled = settings.banner
        self.banner_delay = settings.delay
        self.logger = None
        self.banner_message = settings.banner_message
        self.env_directory = settings.env_directory
        self.json_env = "client_connections.json"
        self.connections_path = os.path.join(self.env_directory, "connections")
        self.json_path = os.path.join(self.connections_path, self.json_env)
        self.webserver_enabled = settings.webserver_enabled
        self.webserver_port = settings.webserver_port
        self.webserver_address = settings.webserver_address
        self.webserver_thread = None    
        self.server_logger = server_logger
        self.app = app
        os.makedirs(self.env_directory, exist_ok=True)
        
        if self.webserver_enabled:
            funnel_logger.info("Webserver enabled.")
            funnel_logger.info(f"Webserver address: {self.webserver_address}")
            funnel_logger.info(f"Webserver port: {self.webserver_port}")
            funnel_logger.info("Starting webserver.")
            self.start_webserver()

    def start_webserver(self):
        from threading import Thread
        from .webserver import app, set_env_directory
        from waitress import serve
        
        def run():
            set_env_directory(self.env_directory)
            self.server_logger.info(f"Webserver running on {self.webserver_address}:{self.webserver_port}")
            serve(self.app, host=self.webserver_address, port=self.webserver_port)

        thread = Thread(target=run, daemon=False, name="webserver")
        
        # Hide output from thread
        thread.start()
        self.webserver_thread = thread            
        

    def start(self):
        server_logger.info("Starting honeypot server.")
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.address, self.port))
        
        self.server_socket.listen(self.concurrent_connections)
        server_logger.info(f"Honeypot server is listening on {self.address}:{self.port}")
        server_logger.info(f"Connection banner enabled: {self.banner_enabled}")
        server_logger.info(f"Connection delay: {self.banner_delay} seconds")
        server_logger.info(f"Concurrent connections allowed: {self.concurrent_connections}")
        if self.username:
            server_logger.info(f"Permitted username: {self.username}")
        if self.password:
            server_logger.info(f"Permitted password: {self.password}")
        
        try:
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    self.client_sockets.append(client_socket)
                    server_logger.info(f"Incoming connection from {addr[0]}:{addr[1]}")
                    self.add_connection(client_ip=addr[0], client_port=addr[1])                    
                    if self.banner_enabled:
                        server_logger.info(f"Sending banner to {addr[0]}:{addr[1]}")
                        banner_message = "Connecting...\n"
                        client_socket.send(banner_message.encode())
                        time.sleep(self.banner_delay)
                        
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    client_thread.start()
                    server_logger.info(f"Started new thread to handle client connection from {addr[0]}:{addr[1]}")
                    self.client_threads.append(client_thread)
                    
                except Exception as error:
                    server_logger.error("Exception - Could not open new client connection")
                    server_logger.error(error)
                    
        except KeyboardInterrupt:
            server_logger.info("Server shutting down.")
            self.stop()
        
    def handle_client(self, client_socket: socket.socket, addr):
        try:
            client_handle(client_socket, addr, self)
        finally:
            client_socket.close()
            server_logger.info(f"Closed connection to {addr[0]}:{addr[1]}")
            
    def stop(self):
        self.running = False
        for client_socket in self.client_sockets:
            try:
                client_socket.close()
            except Exception as e:
                server_logger.error(f"Error closing client socket: {e}")
        if self.server_socket:
            self.server_socket.close()
        for client_thread in self.client_threads:
            client_thread.join()
        
        if self.webserver_thread:
            self.server_logger.info("Webserver has been stopped.")
            for thread in threading.enumerate():
                if thread.name == "webserver":
                    thread.join()
            
        server_logger.info("All connections have been closed.")
        
    def add_connection(self, client_ip, client_port):
        self.__add_connection_count(client_ip=client_ip)
        self.__update_daily_log(client_ip=client_ip, client_port=client_port)
        self.__update_weekly_log(client_ip=client_ip, client_port=client_port)
        self.__update_monthly_log(client_ip=client_ip, client_port=client_port)
        
    def __add_connection_count(self, client_ip):
        # Check if self.env_directory exists and create it if not
        os.makedirs(self.env_directory, exist_ok=True)
        os.makedirs(self.connections_path, exist_ok=True)
        
        # Check if the JSON file exists, create a new one with initial data if not
        if not os.path.exists(self.json_path):
            clients = {
                client_ip: 1
            }
            server_logger.info(f"Created new clients file with initial client: {client_ip}")
        else:
            # Load existing client data from JSON file
            with open(self.json_path, 'r') as json_file:
                clients = json.load(json_file)
            
            # Check if the client_ip already exists, and update the connection count
            if client_ip in clients:
                clients[client_ip] += 1
                server_logger.info(f"Updated connection count for client: {client_ip}")
            else:
                clients[client_ip] = 1
                server_logger.info(f"Added new client: {client_ip}")

        # Write updated client data back to the JSON file
        with open(self.json_path, 'w') as json_file:
            json.dump(clients, json_file, indent=4)
            server_logger.info(f"Saved updated clients data to {self.json_path}")

    def __update_daily_log(self, client_ip, client_port):
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(self.connections_path, exist_ok=True)
        daily_log_filename = os.path.join(self.connections_path, f"connections_{current_date}.json")

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
            "port": client_port,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        daily_log.append(connection_entry)

        # Write updated daily log data back to the JSON file
        with open(daily_log_filename, 'w') as json_file:
            json.dump(daily_log, json_file, indent=4)
            server_logger.info(f"Updated daily log file: {daily_log_filename}")

    def __update_weekly_log(self, client_ip, client_port):
        # Get the start of the current week (Monday)
        current_date = datetime.now()
        start_of_week = (current_date - timedelta(days=current_date.weekday())).strftime("%Y-%m-%d")
        os.makedirs(self.connections_path, exist_ok=True)
        weekly_log_filename = os.path.join(self.connections_path, f"connections_week_{start_of_week}.json")

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
            "port": client_port,
            "timestamp": current_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        weekly_log.append(connection_entry)

        # Write updated weekly log data back to the JSON file
        with open(weekly_log_filename, 'w') as json_file:
            json.dump(weekly_log, json_file, indent=4)
            server_logger.info(f"Updated weekly log file: {weekly_log_filename}")


    def __update_monthly_log(self, client_ip, client_port):
        # Get the current date and month
        current_date = datetime.now()
        month = current_date.strftime("%Y-%m")
        os.makedirs(self.connections_path, exist_ok=True)
        monthly_log_filename = os.path.join(self.connections_path, f"connections_{month}.json")

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
            "port": client_port,
            "timestamp": current_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        monthly_log.append(connection_entry)

        # Write updated monthly log data back to the JSON file
        with open(monthly_log_filename, 'w') as json_file:
            json.dump(monthly_log, json_file, indent=4)
            server_logger.info(f"Updated monthly log file: {monthly_log_filename}")

def honeypot(settings: HoneypotSettings):
    server = HoneypotServer(settings)
    server.start()


# Example usage:
# settings = HoneypotSettings(address="0.0.0.0", port=8022, username="user", password="pass", concurrent_connections=100, banner=True, delay=5)
# honeypot(settings)
