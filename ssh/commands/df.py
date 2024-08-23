def handle(server, command):
    disk_usage = (
        "Filesystem     1K-blocks    Used Available Use% Mounted on\r\n"
        "/dev/sda1      102400000 12345678  89123456  13% /\r\n"
    )
    return f"{disk_usage}".encode('utf-8')

description = "Check disk space usage."
