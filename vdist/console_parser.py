import argparse
import os.path
from typing import Dict


def _check_is_file(_string: str) -> str:
    if os.path.isfile(_string):
        return _string
    else:
        raise argparse.ArgumentTypeError("{0} file does "
                                         "not exists.".format(_string))


# TODO: Some defaults are redundant with defaults at object creation. Fix it.
def parse_arguments(args: list=None) -> Dict[str, str]:
    arg_parser = argparse.ArgumentParser(description="A tool that lets you "
                                                     "create OS packages from "
                                                     "your Python applications "
                                                     "in a clean and self "
                                                     "contained manner.\n",
                                         epilog="Follow vdist development at: "
                                                "<https://github.com/dante-signal31/vdist>")
    # There is a bug in Python 3.5 argparser that makes that missing arguments
    # don't raise a "too few arguments". While that bug is finally fixed, there
    # is a workaround in:
    #   http://stackoverflow.com/questions/23349349/argparse-with-required-subparser
    subparsers = arg_parser.add_subparsers(help="Available modes",
                                           dest="mode")
    subparsers.required = True
    automatic_subparser = subparsers.add_parser("batch",
                                                help="Automatic configuration. "
                                                     "Parameters are going to "
                                                     " be read from a"
                                                     "configuration file.")
    automatic_subparser.add_argument("configuration_file",
                                     nargs="?",
                                     default=None,
                                     type=_check_is_file,
                                     metavar="CONFIGURATION FILENAME")
    # [TODO] Console does not get output_script right when entered from console
    # in batch mode.
    automatic_subparser.add_argument("--output_script",
                                     required=False,
                                     help="Copy build script in output folder.",
                                     action="store_const",
                                     const=True,
                                     default=False)
    manual_subparser = subparsers.add_parser("manual",
                                             help="Manual configuration. "
                                                  "Parameters are going to be "
                                                  "provided through flags.")
    manual_subparser.add_argument("-a", "--app",
                                  required=True,
                                  help="Name of application to package.",
                                  metavar="APP_NAME")
    manual_subparser.add_argument("-v", "--version",
                                  required=True,
                                  help="Version of application to package.",
                                  metavar="APP_VERSION")
    source = manual_subparser.add_mutually_exclusive_group(required=True)
    source.add_argument("-g", "--source_git",
                        help="Location of remote git repository to build from.",
                        metavar="APP_GIT")
    source.add_argument("-G", "--source_git_directory",
                        help="Location of local git repository to build from.",
                        metavar="APP_GIT_DIRECTORY")
    source.add_argument("-d", "--directory",
                        help="Location of local directory to build from.",
                        metavar="APP_DIRECTORY")
    manual_subparser.add_argument("-p", "--profile",
                                  required=True,
                                  help="Build profile",
                                  metavar="BUILD_PROFILE")
    manual_subparser.add_argument("-n", "--name",
                                  required=False,
                                  help="Build name",
                                  metavar="BUILD_NAME")
    manual_subparser.add_argument("-b", "--build_deps",
                                  required=False,
                                  nargs="*",
                                  help="Build dependencies.",
                                  metavar="BUILD_DEPENDENCIES")
    manual_subparser.add_argument("-r", "--runtime_deps",
                                  required=False,
                                  nargs="*",
                                  help="Runtime dependencies.",
                                  metavar="RUNTIME_DEPENDENCIES")
    manual_subparser.add_argument("-c", "--custom_filename",
                                  required=False,
                                  help="Custom filename for generated package.",
                                  metavar="CUSTOM_FILENAME")
    manual_subparser.add_argument("-f", "--fpm_args",
                                  required=False,
                                  help="Extra arguments for FPM. (Put text "
                                       "between quotes)",
                                  metavar="FPM_ARGS")
    manual_subparser.add_argument("-i", "--pip_args",
                                  required=False,
                                  help="Extra arguments for PIP. (Put text "
                                       "between quotes)",
                                  metavar="PIP_ARGS")
    manual_subparser.add_argument("-B", "--python_basedir",
                                  required=False,
                                  help="Base directory were python "
                                       "distribution "
                                       "that is going to be packaged is placed "
                                       "inside container. (Defaults to '/opt')",
                                  metavar="PYTHON_BASEDIR")
    manual_subparser.add_argument("-R", "--package_install_root",
                                  required=False,
                                  help="Base directory were this package "
                                       "is going to be installed in target "
                                       "system. (Defaults to 'python_basedir')",
                                  metavar="INSTALL_ROOT")
    manual_subparser.add_argument("-P", "--package_tmp_root",
                                  required=False,
                                  help="Temporal folder used in docker "
                                       "container to build your package. "
                                       "(Defaults to '/tmp')",
                                  metavar="TMP_ROOT")
    manual_subparser.add_argument("-D", "--working_dir",
                                  required=False,
                                  help="Subdirectory under your source tree "
                                       "that is to be regarded as the base "
                                       "directory",
                                  metavar="WORKING_DIR")
    manual_subparser.add_argument("-C", "--compile_python",
                                  required=False,
                                  help="Indicates Python should be fetched "
                                       "from python.org, compiled and shipped "
                                       "for you.",
                                  action="store_const",
                                  const="True",
                                  default="False")
    manual_subparser.add_argument("-V", "--python_version",
                                  required=False,
                                  help="Python version to package.",
                                  metavar="PYTHON_VERSION")
    manual_subparser.add_argument("-t", "--requirements_path",
                                  required=False,
                                  help="Path to your pip requirements file, "
                                       "relative to your project root. "
                                       "(Defaults to */requirements.txt*).",
                                  metavar="REQUIREMENTS_PATH")
    manual_subparser.add_argument("-o", "--output_folder",
                                  required=False,
                                  help="Folder where generated packages should "
                                       "be placed.",
                                  metavar="OUTPUT_FOLDER")
    manual_subparser.add_argument("--output_script",
                                  required=False,
                                  help="Copy build script in output folder.",
                                  action="store_const",
                                  const=True,
                                  default=False)

    # WARNING: Keep package scripts arguments names similar to fpm arguments for
    # scripts. Arguments names from here are directly used as fpm arguments
    # names.
    manual_subparser.add_argument("--after_install",
                                  required=False,
                                  help="A script to be run after package "
                                       "installation.",
                                  metavar="AFTER_INSTALL_SCRIPT")
    manual_subparser.add_argument("--before_install",
                                  required=False,
                                  help="A script to be run before package "
                                       "installation.",
                                  metavar="BEFORE_INSTALL_SCRIPT")
    manual_subparser.add_argument("--after_remove",
                                  required=False,
                                  help="A script to be run after package "
                                       "removal.",
                                  metavar="AFTER_REMOVE_SCRIPT")
    manual_subparser.add_argument("--before_remove",
                                  required=False,
                                  help="A script to be run before package "
                                       "removal.",
                                  metavar="BEFORE_REMOVE_SCRIPT")
    manual_subparser.add_argument("--after_upgrade",
                                  required=False,
                                  help="A script to be run after package "
                                       "upgrade.",
                                  metavar="AFTER_UPGRADE_SCRIPT")
    manual_subparser.add_argument("--before_upgrade",
                                  required=False,
                                  help="A script to be run before package "
                                       "upgrade",
                                  metavar="BEFORE_UPGRADE_SCRIPT")
    parsed_arguments = vars(arg_parser.parse_args(args))
    filtered_parser_arguments = {key: value for key, value in parsed_arguments.items()
                                 if value is not None}
    return filtered_parser_arguments
