from datetime import datetime, timezone, timedelta

def handle(server, command):
    # Get the current time in UTC
    dt = datetime.now(timezone.utc)
    
    # Format the time in the desired format
    time_str = dt.strftime('%a %b %d %H:%M:%S UTC %Y')
    
    return f"{time_str}\r\n".encode('utf-8')

description = "Get the current date and time."
