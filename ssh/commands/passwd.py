def handle(server, command):
    return f"Sorry, user {server.client_user} is not allowed to execute 'passwd' on {server.hostname}, reporting event.\r\n".encode('utf-8')

description = "Change the password."
