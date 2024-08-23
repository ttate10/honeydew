def handle(server, command):
    return f"{server.hostname}\r\n\r\n".encode('utf-8')

description = "Get the hostname of the current machine."