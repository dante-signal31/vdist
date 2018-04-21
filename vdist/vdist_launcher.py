#!/usr/bin/env python

# Be aware vdist_launcher is designed to be run as an "entry_point", i.e you
# are not supossed to execute python vdist_launcher.py but just vdist command
# after installing vdist package. If you try to run vdist_launcher.py directly
# you are going to get ImportError unless you add vdist main folder (the
# one with setup.py) to PYTHONPATH.

from __future__ import absolute_import

import concurrent.futures as futures
import contextlib
import multiprocessing
import sys
import time

import vdist.console_parser as console_parser
import vdist.configuration as configuration
import vdist.defaults as defaults
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
    arguments.name = defaults.BUILD_NAME
    _configuration = configuration.Configuration(arguments)
    configurations = {defaults.BUILD_NAME: _configuration, }
    return configurations


def run_builds(configurations):
    with futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        workers = []
        for _configuration in configurations:
            print("Starting building process for {0}".format(_configuration))
            worker = executor.submit(builder.build_package, configurations[_configuration])
            workers.append(worker)
            print("Started building process for {0}".format(_configuration))
        print_results(workers)


def print_results(workers):
    for future in futures.as_completed(workers):
        files_created = future.result()
        for worker_name, files in files_created.items():
            print("Files created by {0}:".format(worker_name))
            for file in files:
                print(file)


@contextlib.contextmanager
def time_execution():
    start_time = time.time()
    yield
    execution_time = time.time() - start_time
    print("Total execution time: {0} seconds".format(execution_time))


def main(args=sys.argv[1:]):
    with time_execution():
        console_arguments = console_parser.parse_arguments(args)
        configurations = _get_build_configurations(console_arguments)
        run_builds(configurations)


if __name__ == "__main__":
    main()
