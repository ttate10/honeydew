def handle(server, command):
    args = command.split(" ")
    args.pop(0)
    
    # Default values 
    kernel_name = b"Linux"
    nodename = server.hostname.encode('utf-8')
    kernel_release = b"5.4.0-42-generic"
    kernel_version = b"#46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020"
    machine = b"x86_64"
    processor = b"x86_64"
    hardware_platform = b"x86_64"
    operating_system = b"GNU/Linux"
    
    result = b"" + kernel_name
    # Handle the arguments.
    for arg in args:
        arg = str(arg).lower()
        if arg == "":
            result = b"" + kernel_name
        if arg == "-a":
            result = b"" + kernel_name + b" " + nodename + b" " + kernel_release + b" " + kernel_version + b" " + machine + b" " + processor + b" " + hardware_platform + b" " + operating_system
        elif arg == "-m":
            result = b"" + machine
        elif arg == "-n":
            result = b"" + nodename
        elif arg == "-o":
            result = b"" + operating_system
        elif arg == "-p":
            result = b"" + processor
        elif arg == "-r":
            result = b"" + kernel_release
        elif arg == "-s":
            result = b"" + kernel_name
        elif arg == "-v":
            result = b"" + kernel_version
        else:
            result = b"uname: invalid option -- '" + arg.encode('utf-8') + b"'\r\nusage: uname [-amnoprsv]\r\n"
        
        break
    
    return result + b"\r\n\r\n"

description = "Print system information."
