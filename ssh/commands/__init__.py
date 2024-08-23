import os
import importlib

# Basic dictionary to store the command name and the function to call
command_registry = {}

def load_commands():
    """Load all the commands in the commands directory."""
    for filename in os.listdir(os.path.dirname(__file__)):
        # Check if the file is a python file and not the __init__.py file
        if filename.endswith('.py') and filename != '__init__.py':
            # Import the module and add it to the command registry
            module_name = f"ssh.commands.{filename[:-3]}"
            # Import the module
            module = importlib.import_module(module_name)
            # Add the module to the command registry
            command_registry[module_name.split('.')[-1]] = (module.handle, module.description)

# Load all the commands
load_commands()
