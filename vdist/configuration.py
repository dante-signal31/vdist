import configparser
from typing import Dict

import vdist.defaults as defaults
import vdist.source as source

LISTABLE_ARGUMENTS = {"source_git", "source_git_directory", "runtime_deps",
                      "build_deps"}
LONG_TEXT_ARGUMENTS = {"fpm_args", "pip_args"}
PROCESSABLE_ARGUMENTS = {"source_directory", "compile_python",
                         "fpm_args"}
SCRIPTS_ARGUMENTS = {"after_install", "before_install", "after_remove",
                     "before_remove", "after_upgrade", "before_upgrade"}
USELESS_ARGUMENTS = {"mode", "name", "output_folder", "output_script"}
PROCESSABLE_ARGUMENTS |= LISTABLE_ARGUMENTS
PROCESSABLE_ARGUMENTS |= LONG_TEXT_ARGUMENTS


class Configuration(object):

    # Using a fixed set of parameters for __init__ might be cleaner here but
    # I've found it less scalable in this specific case. After many test I
    # feel better for scalation using a generic dir as input and process it
    # using various arguments sets, it keeps my __init_ shorter and it is easier
    # add and remove arguments.
    def __init__(self, arguments):
        self.output_folder = arguments.get("output_folder",
                                           defaults.OUTPUT_FOLDER)
        self.output_script = arguments.get("output_script",
                                           defaults.OUTPUT_SCRIPT)
        self.name = arguments.get("name", defaults.BUILD_NAME)
        self.builder_parameters = {key: value for key, value in arguments.items()
                                   if key not in PROCESSABLE_ARGUMENTS and
                                   key not in USELESS_ARGUMENTS}
        self._process_listable_arguments(arguments)
        self._process_long_text_arguments(arguments)
        self._process_source_directory_argument(arguments)
        self._process_compile_python_argument(arguments)

    def _process_source_directory_argument(self, arguments):
        if "source_directory" in arguments.keys():
            directory = arguments["source_directory"]
            directory = directory.strip()
            self.builder_parameters["source"] = source.directory(directory)

    def _process_compile_python_argument(self, arguments):
        if "compile_python" in arguments.keys():
            self.builder_parameters["compile_python"] = bool(
                arguments["compile_python"])

    def _process_listable_arguments(self, arguments):
        argument_keys = set(arguments.keys())
        listable_arguments_found = LISTABLE_ARGUMENTS.intersection(argument_keys)
        for argument in listable_arguments_found:
            generated_list = _create_list(arguments[argument])
            if argument == "source_git":
                self.builder_parameters["source"] = source.git(
                    generated_list[0],
                    generated_list[1])
            if argument == "source_git_directory":
                self.builder_parameters["source"] = source.git_directory(
                    generated_list[0],
                    generated_list[1])
            if argument in ["runtime_deps", "build_deps"]:
                self.builder_parameters[argument] = generated_list

    def _process_long_text_arguments(self, arguments):
        argument_keys = set(arguments.keys())
        long_text_arguments_found = LONG_TEXT_ARGUMENTS.intersection(
            argument_keys)
        for argument in long_text_arguments_found:
            text_with_no_cr = _remove_cr(arguments[argument])
            self.builder_parameters[argument] = text_with_no_cr


def _create_list(_list):
    return _list if isinstance(_list, list) else [element.strip()
                                                  for element in _list.split(",")]


def _remove_cr(text):
    # Removes carriage returns from given text.
    # Great reference:
    #   http://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python
    #   http://stackoverflow.com/questions/21038891/what-does-table-in-the-string-translate-function-mean
    return text.translate({ord('\n'): ord(' '), })


def read(configuration_file: str) -> Dict[str, Configuration]:
    # Should return a dict whose keys should be configfile sections
    # (except DEFAULT) and configurations objects as values.
    parser = _get_config_parser()
    parser.read(configuration_file)
    configurations = {}
    for section in parser.sections():
        parameters = _get_section_values(parser, section)
        parameters["name"] = section
        configurations[section] = Configuration(parameters)
    return configurations


def _get_section_values(parser, section):
    section_values = {key: parser[section][key]
                      for key in parser[section]}
    return section_values


def _get_config_parser():
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    return parser

