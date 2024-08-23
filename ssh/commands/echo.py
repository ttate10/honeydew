def handle(server, command):
    # Remove 'echo' from the command to get the message
    message = command[5:]  
    return f"{message}\r\n".encode('utf-8')

description = "Echo a message back to the user."