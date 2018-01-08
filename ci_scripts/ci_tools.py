# Common functions used by ci scripts.
import sys
import subprocess


def run_console_command(command):
    if sys.version_info.major < 3:
        subprocess.call(command, shell=True)
    else:
        subprocess.run(command, shell=True, check=True)