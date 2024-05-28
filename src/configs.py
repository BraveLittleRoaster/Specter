import os
from rich.console import Console

console = Console()

# Log info
log_info = "[#0079FF][-][/]"
log_success = "[#00DFA2][+][/]"
log_warn = "[#F6FA70][~][/]"
log_error = "[#FF0060 blink bold][!]"
# Filepaths
home_path = os.path.expanduser("~")
config_dir = f"{home_path}/.config"
root_dir = f"{config_dir}/Specter"
