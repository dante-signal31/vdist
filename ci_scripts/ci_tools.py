# Common functions used by ci scripts.
import os
import sys
import subprocess
if sys.version_info.major < 3:
    import ConfigParser as configparser
else:
    import configparser


def get_current_version(configuration_file):
    parser = _get_config_parser()
    parser.read(configuration_file)
    version = _get_version(parser)
    return version


def get_environment_value(variable_name):
    return os.environ[variable_name]


def set_environment_value(variable_name, variable_value):
    os.environ[variable_name] = variable_value


def _get_config_parser():
    if sys.version_info[0] == 3:
        parser = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
    else:
        parser = configparser.ConfigParser()
    return parser


def _get_version(parser):
    if sys.version_info[0] == 3:
        version = parser["DEFAULT"]["version"]
    else:
        version = parser.get("DEFAULT", "version")
    return version


def run_console_command(command):
    if sys.version_info.major < 3:
        subprocess.call(command, shell=True)
    else:
        subprocess.run(command, shell=True, check=True)