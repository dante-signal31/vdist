#!/usr/bin/env python

# Be aware vdist_launcher is designed to be run as an "entry_point", i.e you
# are not supossed to execute python vdist_launcher.py but just vdist command
# after installing vdist package. If you try to run vdist_launcher.py directly
# you are going to get ImportError unless you add vdist main folder (the
# one with setup.py) to PYTHONPATH.
import concurrent.futures as futures
import contextlib
import multiprocessing
import sys
import time
import traceback
from typing import Dict, List

import vdist.console_parser as console_parser
import vdist.configuration as configuration
import vdist.defaults as defaults
import vdist.builder as builder


def _get_build_configurations(arguments: Dict[str, str]) -> Dict[str, configuration.Configuration]:
    try:
        if arguments["configuration_file"] is None:
            configurations = _load_default_configuration(arguments)
        else:
            configurations = configuration.read(arguments["configuration_file"])
    except KeyError:
        configurations = _load_default_configuration(arguments)
    return configurations


def _load_default_configuration(arguments: Dict[str, str]) -> Dict[str, configuration.Configuration]:
    arguments.name = defaults.BUILD_NAME
    _configuration = configuration.Configuration(arguments)
    configurations = {defaults.BUILD_NAME: _configuration, }
    return configurations


def run_builds(configurations: Dict[str, configuration.Configuration]) -> None:
    with futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        workers = []
        for _configuration in configurations:
            print(f"Starting building process for {_configuration}")
            worker = executor.submit(builder.build_package, configurations[_configuration])
            workers.append(worker)
            print(f"Started building process for {_configuration}")
        print_results(workers)


def print_results(workers: List[futures.Executor]) -> None:
    for future in futures.as_completed(workers):
        files_created = future.result()
        for worker_name, files in files_created.items():
            print(f"Files created by {worker_name}:")
            for file in files:
                print(file)


@contextlib.contextmanager
def time_execution():
    start_time = time.time()
    yield
    execution_time = time.time() - start_time
    print(f"Total execution time: {execution_time} seconds")


def main(args: List=sys.argv[1:]) -> None:
    try:
        with time_execution():
            console_arguments = console_parser.parse_arguments(args)
            configurations = _get_build_configurations(console_arguments)
            run_builds(configurations)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
