#!/bin/zsh
# Check if the Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found"
    exit 1
fi

# Check if main.py is present
if [ ! -f "main.py" ]; then
    echo "main.py not found"
    exit 1
fi

# Check if server.key is present
if [ ! -f "server.key" ]; then
    echo "server.key not found, the script will automatically generate a host key."
fi

# Start the SSH honeypot
echo "StartupScript: Starting SSH Honeypot"
python3 main.py -a 0.0.0.0 -p 8022 --banner -w password
