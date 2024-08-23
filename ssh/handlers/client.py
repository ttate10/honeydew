import paramiko
import ssh
from honeypot.logger import funnel_logger, server_logger

def client_handle(client, addr, honeypot_server) -> None: 
    """Handle the client connection."""
    client_ip = addr[0]
    username = honeypot_server.username 
    password = honeypot_server.password 
    hostname = honeypot_server.hostname 
    env_directory = honeypot_server.env_directory
    banner_message = honeypot_server.banner_message
    
    try:
        transport = paramiko.Transport(client)  
        transport.local_version = "SSH-2.0-MySSHServer_1.0"
        
        # Create a new instance of the Server class.
        server = ssh.Server(client_ip=client_ip, input_username=username, input_password=password, hostname=hostname, env_directory=env_directory)
        
        # Add the host key to the server.
        transport.add_server_key(server.host_key)
        transport.start_server(server=server)
        
        # Establish the connection.
        channel = transport.accept(100)
        
        if channel is None:
            funnel_logger.error(f"Client {client_ip} failed to open a channel.")
            server_logger.error(f"Client {client_ip} failed to open a channel.")
            return
        
        try:
            # Send a generic welcome banner to the client.
            channel.send(banner_message)
            
            ssh.handlers.shell_handle(channel, server=server, client_ip=client_ip)
            server_logger.info(f"Client {client_ip} disconnected from server.")
            
        except Exception as error:
            print(error)
            
    except Exception as error:
        print(error)

    finally:
        try:
            transport.close()
        except Exception:
            pass
        
        client.close()
                    
            