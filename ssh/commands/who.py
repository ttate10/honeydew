def handle(server, command):
    """Print current connected user and time."""
    response = (
        b""
        + "{:<10} {:<10} {:<20}".format("root", "console", "Jan 10 22:01").encode('utf-8')
        + b"\r\n"
        + "{:<10} {:<10} {:<20}".format(server.client_user, "ttys006", server.connected_time.strftime("%b %d %H:%M")).encode('utf-8')
        + b"\r\n"
        + b"\r\n"
    ) 

    return response

description = "See current logged in users."
