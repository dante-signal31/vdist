#!/usr/bin/env python

# Be aware vdist_launcher is designed to be run as an "entry_point", i.e you
# are not supossed to execute python vdist_launcher.py but just vdist command
# after installing vdist package. If you try to run vdist_launcher.py directly
# you are going to get ImportError unless you add vdist main folder (the
# one with setup.py) to PYTHONPATH.

from __future__ import absolute_import

import concurrent.futures
import sys

import vdist.console_parser as console_parser
import vdist.configuration as configuration
import vdist.builder as builder


def _get_build_configurations(arguments):
    try:
        if arguments["configuration_file"] is None:
            configurations = _load_default_configuration(arguments)
        else:
            configurations = configuration.read(arguments["configuration_file"])
    except KeyError:
        configurations = _load_default_configuration(arguments)
    return configurations


def _load_default_configuration(arguments):
    _configuration = configuration.Configuration(arguments)
    configurations = {"Default project": _configuration, }
    return configurations


def main(args=sys.argv[1:]):
    console_arguments = console_parser.parse_arguments(args)
    configurations = _get_build_configurations(console_arguments)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for _configuration in configurations:
            executor.submit(builder.build_package,
                            configurations[_configuration])


if __name__ == "__main__":
    main()
