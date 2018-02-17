import contextlib
import copy
import os.path
import pytest
import sys
import tempfile

import tests.testing_tools as testing_tools
import vdist.builder as builder
import vdist.console_parser as console_parser
import vdist.configuration as configuration
import vdist.source as source
import vdist.vdist_launcher as vdist_launcher


# Python 2.x ConfigParser lacks of extended interpolation support and its
# tag format changes, so you should alter your config text depending whether
# you are building with Python 3 or not.
if sys.version_info[0] == 3:
    DUMMY_CONFIGURATION_TEXT = """[DEFAULT]
    app = geolocate
    version = 1.3.0
    source_git = https://github.com/dante-signal31/${app}, master
    fpm_args = --maintainer dante.signal31@gmail.com -a native --url
        https://github.com/dante-signal31/${app} --description
        "This program accepts any text and searchs inside every IP
        address. With each of those IP addresses,
        ${app} queries
        Maxmind GeoIP database to look for the city and
        country where
        IP address or URL is located. Geolocate is designed to be
        used in console with pipes and redirections along with
        applications like traceroute, nslookup, etc."
        --license BSD-3 --category net
    requirements_path = /REQUIREMENTS.txt
    runtime_deps = libssl1.0.0, dummy1.0.0
    compile_python = True
    python_version = 3.4.4
    output_folder = ./vdist
    after_install = packaging/postinst.sh
    after_remove = packaging/postuninst.sh

    [Ubuntu-package]
    profile = ubuntu-trusty

    [Centos7-package]
    profile = centos7
    """
else:
    # Whereas Python 3's one, Python 2's configparser does not remove tabs
    # beginning a line, so don't add a tab to this tab to fix indentation or
    # tests will probably fail miserably.
    DUMMY_CONFIGURATION_TEXT = """[DEFAULT]
app = geolocate
version = 1.3.0
source_git = https://github.com/dante-signal31/%(app)s, master
fpm_args = --maintainer dante.signal31@gmail.com -a native --url
    https://github.com/dante-signal31/%(app)s --description
    "This program accepts any text and searchs inside every IP
    address. With each of those IP addresses,
    %(app)s queries
    Maxmind GeoIP database to look for the city and
    country where
    IP address or URL is located. Geolocate is designed to be
    used in console with pipes and redirections along with
    applications like traceroute, nslookup, etc."
    --license BSD-3 --category net
requirements_path = /REQUIREMENTS.txt
runtime_deps = libssl1.0.0, dummy1.0.0
compile_python = True
python_version = 3.4.4
output_folder = ./vdist
after_install = packaging/postinst.sh
after_remove = packaging/postuninst.sh

[Ubuntu-package]
profile = ubuntu-trusty

[Centos7-package]
profile = centos7
"""

DUMMY_OUTPUT_FOLDER = "/tmp/vdist-tests"

UBUNTU_ARGPARSED_ARGUMENTS = {
    "mode": "manual",
    "app": 'geolocate',
    "version": '1.3.0',
    "source_git": "https://github.com/dante-signal31/geolocate, master",
    "profile": 'ubuntu-trusty',
    "compile_python": "True",
    "python_version": '3.4.4',
    "fpm_args": '--maintainer dante.signal31@gmail.com -a native --url '
                'https://github.com/dante-signal31/geolocate --description '
                '"This program accepts any text and searchs inside every IP'
                ' address. With each of those IP addresses, '
                'geolocate queries '
                'Maxmind GeoIP database to look for the city and '
                'country where'
                ' IP address or URL is located. Geolocate is designed to be'
                ' used in console with pipes and redirections along with '
                'applications like traceroute, nslookup, etc."'
                ' --license BSD-3 --category net',
    "requirements_path": '/REQUIREMENTS.txt',
    "runtime_deps": ["libssl1.0.0", "dummy1.0.0"],
    "output_folder": DUMMY_OUTPUT_FOLDER,
    "after_install": 'packaging/postinst.sh',
    "after_remove": 'packaging/postuninst.sh',
    "output_script": False
}


CORRECT_UBUNTU_PARAMETERS = {
    "app": 'geolocate',
    "version": '1.3.0',
    "source": source.git(
        uri='https://github.com/dante-signal31/geolocate',
        branch='master'
    ),
    "profile": 'ubuntu-trusty',
    "compile_python": True,
    "python_version": '3.4.4',
    "fpm_args": '--maintainer dante.signal31@gmail.com -a native --url '
                'https://github.com/dante-signal31/geolocate --description '
                '"This program accepts any text and searchs inside every IP'
                ' address. With each of those IP addresses, '
                'geolocate queries '
                'Maxmind GeoIP database to look for the city and '
                'country where'
                ' IP address or URL is located. Geolocate is designed to be'
                ' used in console with pipes and redirections along with '
                'applications like traceroute, nslookup, etc."'
                ' --license BSD-3 --category net',
    "requirements_path": '/REQUIREMENTS.txt',
    "runtime_deps": ["libssl1.0.0", "dummy1.0.0"],
    "after_install": 'packaging/postinst.sh',
    "after_remove": 'packaging/postuninst.sh'
}

DUMMY_PACKAGE_NAME = "geolocate-1.3.0-ubuntu-trusty"
DUMMY_PACKAGE_EXTENSION = ".deb"
DUMMY_CONFIGURATION_ARGUMENTS = copy.deepcopy(CORRECT_UBUNTU_PARAMETERS)
DUMMY_CONFIGURATION_ARGUMENTS["output_folder"] = DUMMY_OUTPUT_FOLDER
DUMMY_CONFIGURATION = configuration.Configuration(UBUNTU_ARGPARSED_ARGUMENTS)
CORRECT_OUTPUT_FOLDER = "./vdist"
DUMMY_CONFIGURATION_FILE_ARGUMENTS = ["batch", "config.cfg"]
DUMMY_MANUAL_ARGUMENTS = ["manual",
                          "--app", "geolocate",
                          "--version", "1.3.0",
                          "--source_git", "https://github.com/dante-signal31/geolocate, master",
                          "--profile", "ubuntu-trusty",
                          "--compile_python",
                          "--python_version", "3.4.4",
                          "--fpm_args", '--maintainer dante.signal31@gmail.com -a native --url '
                                        'https://github.com/dante-signal31/geolocate --description '
                                        '"This program accepts any text and searchs inside every IP'
                                        ' address. With each of those IP addresses, '
                                        'geolocate queries '
                                        'Maxmind GeoIP database to look for the city and '
                                        'country where'
                                        ' IP address or URL is located. Geolocate is designed to be'
                                        ' used in console with pipes and redirections along with '
                                        'applications like traceroute, nslookup, etc."'
                                        ' --license BSD-3 --category net',
                          "--requirements_path", "/REQUIREMENTS.txt",
                          "--runtime_deps", "libssl1.0.0", "dummy1.0.0",
                          "--output_folder", DUMMY_OUTPUT_FOLDER,
                          "--after_install", 'packaging/postinst.sh',
                          "--after_remove", 'packaging/postuninst.sh']
DUMMY_MANUAL_ARGUMENTS_OUTPUT_SCRIPT = list(DUMMY_MANUAL_ARGUMENTS)
DUMMY_MANUAL_ARGUMENTS_OUTPUT_SCRIPT.append("--output_script")


@contextlib.contextmanager
def _create_dummy_configuration_file(configuration_text):
    with tempfile.NamedTemporaryFile(mode="wb") as temporary_file:
        temporary_file.write(configuration_text.encode("UTF-8"))
        temporary_file.flush()
        yield temporary_file


def test_configuration_file_read():
    with _create_dummy_configuration_file(DUMMY_CONFIGURATION_TEXT) as config_file:
        configurations = configuration.read(config_file.name)
        ubuntu_configuration = configurations["Ubuntu-package"]
        assert ubuntu_configuration.builder_parameters == CORRECT_UBUNTU_PARAMETERS
        assert ubuntu_configuration.output_folder == CORRECT_OUTPUT_FOLDER
        assert "Centos7-package" in configurations


def test_parse_arguments():
    # Batch mode
    parsed_arguments = console_parser.parse_arguments(["batch", "/etc/passwd"])
    assert parsed_arguments["configuration_file"] == "/etc/passwd" \
           and not parsed_arguments["output_script"]

    # Manual mode
    parsed_arguments = console_parser.parse_arguments(DUMMY_MANUAL_ARGUMENTS)
    assert parsed_arguments == UBUNTU_ARGPARSED_ARGUMENTS \
           and not parsed_arguments["output_script"]
    # Output script
    parsed_arguments = console_parser.parse_arguments(["batch",
                                                       "/etc/passwd",
                                                       "--output_script"])
    assert parsed_arguments["configuration_file"] == "/etc/passwd" \
           and parsed_arguments["output_script"]
    parsed_arguments = console_parser.parse_arguments(DUMMY_MANUAL_ARGUMENTS_OUTPUT_SCRIPT)
    assert parsed_arguments == UBUNTU_ARGPARSED_ARGUMENTS_OUTPUT_SCRIPT \
           and parsed_arguments["output_script"]


def test_move_package_to_output_folder():
    temporary_directory = testing_tools.get_temporary_directory_context_manager()
    with temporary_directory() as tempdir:
        package_folder = os.path.join(tempdir, DUMMY_PACKAGE_NAME)
        os.mkdir(package_folder)
        with tempfile.NamedTemporaryFile(prefix=DUMMY_PACKAGE_NAME,
                                         suffix=DUMMY_PACKAGE_EXTENSION,
                                         dir=package_folder) as dummy_package:
            dummy_source_folder, dummy_package_name = os.path.split(dummy_package.name)
            builder._move_package_to_output_folder(DUMMY_CONFIGURATION,
                                                   source_folder=tempdir)
            correct_package = os.path.join(DUMMY_OUTPUT_FOLDER,
                                           dummy_package_name)
            assert os.path.isfile(correct_package)


@pytest.mark.slow
def test_build_package_batch():
    with _create_dummy_configuration_file(DUMMY_CONFIGURATION_TEXT) as config_file:
        configurations = configuration.read(config_file.name)
        _generate_packages(configurations)


@pytest.mark.slow
def test_build_package_manual():
    console_arguments = console_parser.parse_arguments(DUMMY_MANUAL_ARGUMENTS)
    configurations = vdist_launcher._get_build_configurations(console_arguments)
    _generate_packages(configurations)


def _generate_packages(configurations):
    for package_configuration in configurations.values():
        builder.build_package(package_configuration)
        correct_output_package = os.path.join(
            package_configuration.output_folder,
            _get_correct_package_name(package_configuration))
        assert os.path.isfile(correct_output_package)


def _get_correct_package_name(_configuration):
    profile = _configuration.builder_parameters["profile"]
    package_name = None
    if profile == "ubuntu-trusty":
        package_name = "_".join([_configuration.builder_parameters["app"],
                                 _configuration.builder_parameters["version"],
                                 'amd64.deb'])
    elif profile == "centos6" or profile == "centos7":
        package_name = "-".join([_configuration.builder_parameters["app"],
                                 _configuration.builder_parameters["version"],
                                '1.x86_64.rpm'])
    else:
        raise UnknownProfile(profile)
    return package_name


class Error(Exception):
    pass


class UnknownProfile(Error):

    def __init__(self, tried_profile):
        super(UnknownProfile, self).__init__()
        self.messsage = "Tried profile: {0}".format(tried_profile)


