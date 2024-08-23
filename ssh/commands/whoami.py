def handle(server, command):
    return f"{server.client_user}\r\n\r\n".encode('utf-8')

description = "Print the user name."
