from datetime import datetime

def handle(server, command):
    start_time = server.random_server_start_timem
    current_time = datetime.now()

    uptime = current_time - start_time

    return f"System has been running for {uptime.days} days, {uptime.seconds // 3600} hours, {uptime.seconds // 60 % 60} minutes, {uptime.seconds % 60} seconds.\r\n".encode('utf-8')
description = "Check how long the system has been running."
