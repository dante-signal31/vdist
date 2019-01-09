# Common functions used by ci scripts.
import os
import sys
import subprocess
import contextlib
if sys.version_info.major < 3:
    import ConfigParser as configparser
else:
    import configparser


@contextlib.contextmanager
def read_configuration(configuration_file):
    parser = _get_config_parser()
    parser.read_file(open(configuration_file))
    yield parser


def get_current_version(configuration_file):
    with read_configuration(configuration_file) as parser:
        version = _get_value(parser, "DEFAULT", "version")
        return version


def get_python_version_to_package(configuration_file):
    with read_configuration(configuration_file) as parser:
        python_version = _get_value(parser, "DEFAULT", "python_version")
        python_version_parts = python_version.split(".")
        return "{}.{}".format(python_version_parts[0], python_version_parts[1])


def get_app_name(configuration_file):
    with read_configuration(configuration_file) as parser:
        app_name = _get_value(parser, "DEFAULT", "app")
        return app_name


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


def _get_value(parser, section, parameter):
    if sys.version_info[0] == 3:
        value = parser[section][parameter]
    else:
        value = parser.get(section, parameter)
    return value


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
