# Common functions used by ci scripts.
import subprocess


def run_console_command(command: str)-> None:
    subprocess.run(command, shell=True, check=True)