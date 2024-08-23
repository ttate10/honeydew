from datetime import datetime

def handle(server, command):
    start_time = server.start_time
    current_time = datetime.now()
    
    uptime = current_time - start_time
    
    # Calculate the total number of seconds in the uptime
    total_seconds = int(uptime.total_seconds())
    
    # Calculate hours, minutes, and seconds from total seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # Format the process list with the calculated uptime
    process_list = (
        "{:<4} {:<7} {:<20}".format("USER", "TTY", "TIME") + "\r\n"
        f"1203 ttys006 {hours:02}:{minutes:02}:{seconds:02} /bin/zsh -i\r\n"
    )
    
    return f"{process_list}".encode('utf-8')

description = "List currently running processes."
