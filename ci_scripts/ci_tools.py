# Common functions used by ci scripts.
import subprocess


def run_console_command(command):
    subprocess.run(command, shell=True, check=True)