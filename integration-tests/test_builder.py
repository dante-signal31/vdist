import os
import re
import subprocess

import pytest

import tests.test_console_launcher as test_console
import tests.testing_tools as testing_tools
import ci_scripts.ci_tools as ci_tools

import vdist.configuration as configuration
import vdist.console_parser as console_parser
import vdist.builder as builder
import vdist.vdist_launcher as launcher
from vdist.source import git, git_directory, directory

DEB_COMPILE_FILTER = [r'[^\.]', r'\./$', r'\./usr/', r'\./opt/$']
DEB_NOCOMPILE_FILTER = [r'[^\.]', r'^\.\.', r'\./$', r'^\.$', r'\./opt/$',
                        r'\./root/$',
                        r'\./usr/$', r'\./usr/share/$', r'\./usr/share/doc/$',
                        r'\./usr/share/doc/geolocate/$',
                        r'\./usr/share/doc/geolocate/changelog.gz$']
RPM_COMPILE_FILTER = [r'\/usr/lib/.build-id']
PKG_COMPILE_FILTER = [r'.MKTREE',
                      r'.PKGINFO',
                      r'.BUILDINFO']

FPM_ARGS_GEOLOCATE = '--maintainer dante.signal31@gmail.com -a native --url ' \
           'https://github.com/dante-signal31/geolocate --description ' \
           '"This program accepts any text and searchs inside every IP' \
           ' address. With each of those IP addresses, ' \
           'geolocate queries ' \
           'Maxmind GeoIP database to look for the city and ' \
           'country where' \
           ' IP address or URL is located. Geolocate is designed to be' \
           ' used in console with pipes and redirections along with ' \
           'applications like traceroute, nslookup, etc.' \
           ' " --license BSD-3 --category net '
FPM_ARGS_VDIST = '--maintainer dante.signal31@gmail.com -a native ' \
                 '--url https://github.com/dante-signal31/${app} ' \
                 '--description "vdist (Virtualenv Distribute) is a ' \
                 'tool that lets you build OS packages from your ' \
                 'Python applications, while aiming to build an isolated ' \
                 'environment for your Python project by utilizing ' \
                 'virtualenv. This means that your application will ' \
                 'not depend on OS provided packages of Python modules, ' \
                 'including their versions." --license MIT --category net'

TEST_CONFIGURATION_FILE = """
[DEFAULT]
app = vdist
# All version tags, even bintray json descriptors, are automatically updated from next value.
version = 1.1.0
# source_git = https://github.com/dante-signal31/${app}, vdist_tests
source_git = https://github.com/dante-signal31/${app}, fix_scripts
fpm_args = --maintainer dante.signal31@gmail.com -a native --url
    https://github.com/dante-signal31/${app} --description
    "vdist (Virtualenv Distribute) is a tool that lets you build OS packages
     from your Python applications, while aiming to build an
     isolated environment for your Python project by utilizing virtualenv. This
     means that your application will not depend on OS provided packages of
     Python modules, including their versions."
    --license MIT --category net
requirements_path = ./requirements.txt
compile_python = True
python_version = 3.7.5
output_folder = ./package_dist/
after_install = packaging/postinst.sh
after_remove = packaging/postuninst.sh

[Ubuntu-package]
profile = ubuntu-lts
runtime_deps = libssl1.0.0, docker-ce

# [Centos-package]
# profile = centos
# runtime_deps = openssl, docker-ce
# 
# [Archlinux-package]
# profile = archlinux
# runtime_deps = openssl, docker
"""

VDIST_GITHUB_REPOSITORY = 'https://github.com/dante-signal31/vdist'
VDIST_TEST_BRANCH = "vdist_tests"

temporary_directory = testing_tools.get_temporary_directory_context_manager()


def _get_package_file_list(file_name):
    readers = {
        "deb": _read_deb_contents,
        "rpm": _read_rpm_contents,
        "xz": _read_pkg_contents
    }
    file_extension = os.path.splitext(file_name)[1].lstrip(".")
    return readers[file_extension](file_name)


def _read_deb_contents(deb_file_pathname):
    entries = os.popen("dpkg -c {0}".format(deb_file_pathname)).readlines()
    file_list = [entry.split()[-1] for entry in entries]
    return file_list


def _read_rpm_contents(rpm_file_pathname):
    entries = os.popen("rpm -qlp {0}".format(rpm_file_pathname)).readlines()
    file_list = [entry.rstrip("\n") for entry in entries
                 if entry.startswith("/")]
    return file_list


def _read_pkg_contents(pkg_file_pathname):
    entries = os.popen("tar -Jtf {0}".format(pkg_file_pathname)).readlines()
    file_list = ["/".join(["", entry]).rstrip("\n") for entry in entries
                 if not entry.startswith(".")]
    return file_list


def _purge_list(original_list, purgables):
    list_purged = []
    for entry in original_list:
        entry_free_of_purgables = all(True if re.match(pattern, entry) is None
                                      else False
                                      for pattern in purgables)
        if entry_free_of_purgables:
            list_purged.append(entry)
    return list_purged


def _call_builder(builder_parameters):
    _configuration = configuration.Configuration(builder_parameters)
    builder.build_package(_configuration)


def _generate_rpm(builder_parameters):
    _call_builder(builder_parameters)
    rpm_filename_prefix = "-".join([builder_parameters["app"],
                                    builder_parameters["version"]])
    target_file = os.path.join(
        builder_parameters["output_folder"],
        "".join([rpm_filename_prefix, '-1.x86_64.rpm']),
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    return target_file


def _generate_deb(builder_parameters):
    _call_builder(builder_parameters)
    deb_filename_prefix = "_".join([builder_parameters["app"],
                                    builder_parameters["version"]])
    target_file = os.path.join(builder_parameters["output_folder"],
                               "".join([deb_filename_prefix, '_amd64.deb']))
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    return target_file


def _generate_pkg(builder_parameters):
    _call_builder(builder_parameters)
    pkg_filename_prefix = "-".join([builder_parameters["app"],
                                    builder_parameters["version"]])
    target_file = os.path.join(builder_parameters["output_folder"],
                               "".join([pkg_filename_prefix, '-1-x86_64.pkg.tar.xz']))
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
    return target_file


def _get_purged_file_list(filepath, file_filter):
    file_list = _get_package_file_list(filepath)
    file_list_purged = _purge_list(file_list, file_filter)
    return file_list_purged


# def _get_purged_deb_file_list(deb_filepath, file_filter):
#     file_list = _read_deb_contents(deb_filepath)
#     file_list_purged = _purge_list(file_list, file_filter)
#     return file_list_purged
#
#
# def _get_purged_rpm_file_list(rpm_filepath, file_filter):
#     file_list = _read_rpm_contents(rpm_filepath)
#     file_list_purged = _purge_list(file_list, file_filter)
#     return file_list_purged

def _get_builder_parameters(app_name, profile_name, temp_dir, output_dir):
    builder_configurations = {
        ## TODO: Some tests fail if I leave app_name at "app" but not hardcode it. Give it a second thought and leave coherent.
        ## TODO: To much code redundancy in these configurations. See how to reduce it.
        "vdist-test-generate-deb-from-dir": {
            "app": app_name,
            "version": '1.0',
            "source": directory(path=temp_dir, ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        'vdist-test-generate-rpm-from-dir': {
            "app": 'vdist-test-generate-rpm-from-dir',
            "version": '1.0',
            "source": directory(path=temp_dir, ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-pkg-from-dir": {
            "app": app_name,
            "version": '1.0',
            "source": directory(path=temp_dir, ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-deb-from-git-dir": {
            "app": app_name,
            "version": '1.0',
            "source": git_directory(path=temp_dir,
                                    branch='vdist_tests'),
            "profile": 'ubuntu-lts',
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-rpm-from-git-dir": {
            "app": app_name,
            "version": '1.0',
            "source": git_directory(path=temp_dir,
                                    branch='vdist_tests'),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-pkg-from-git-dir": {
            "app": app_name,
            "version": '1.0',
            "source": git_directory(path=temp_dir,
                                    branch='vdist_tests'),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-deb-from-git-suffixed": {
            "app": app_name,
            "version": '1.0',
            "source": git(
                uri='https://github.com/dante-signal31/vdist.git',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-rpm-from-git-suffixed": {
            "app": app_name,
            "version": '1.0',
            "source": git(
                uri='https://github.com/dante-signal31/vdist.git',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-pkg-from-git-suffixed": {
            "app": app_name,
            "version": '1.0',
            "source": git(
                uri='https://github.com/dante-signal31/vdist.git',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        },
        "jtrouble_nosetup_nocompile": {
            "app": 'jtrouble',
            "version": '1.0.0',
            "source": git(
                uri='https://github.com/objectified/jtrouble',
                branch='master'
            ),
            "profile": profile_name,
            "compile_python": False,
            # Here happens the same than in
            # test_generate_deb_from_git_setup_nocompile()
            # "python_version": '3.4.4',
            "python_basedir": '/root/custom_python',
            "output_folder": output_dir,
            "output_script": True
        },
        "geolocate-test-generate-deb-from-git-setup-nocompile": {
            "app": 'geolocate',
            "version": '1.4.1',
            "source": git(
                uri='https://github.com/dante-signal31/geolocate',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "compile_python": False,
            # "python_version": '3.5.3',
            # Lets suppose custom python package is already installed and its root
            # folder is /root/custom_python.
            "python_basedir": '/root/custom_python',
            "fpm_args": FPM_ARGS_GEOLOCATE,
            "requirements_path": '/REQUIREMENTS.txt',
            "build_deps": ["python3-all-dev", "build-essential", "libssl-dev",
                           "pkg-config", "libdbus-glib-1-dev", "gnome-keyring",
                           "libffi-dev"],
            "runtime_deps": ["libssl1.0.0", "python3-dbus", "gnome-keyring"],
            "after_install": 'packaging/postinst.sh',
            "after_remove": 'packaging/postuninst.sh',
            "output_folder": output_dir,
            "output_script": True
        },
        "geolocate-test_generate_rpm_from_git_setup_nocompile_centos": {
            "app": 'geolocate',
            "version": '1.4.1',
            "source": git(
                uri='https://github.com/dante-signal31/geolocate',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "compile_python": False,
            # "python_version": '3.4.4',
            # Lets suppose custom python package is already installed and its root
            # folder is '/root/custom_python'.
            "python_basedir": '/root/custom_python',
            "fpm_args": FPM_ARGS_GEOLOCATE,
            "requirements_path": '/REQUIREMENTS.txt',
            "build_deps": ["python3-all-dev", "build-essential", "libssl-dev",
                           "pkg-config", "libdbus-glib-1-dev", "gnome-keyring",
                           "libffi-dev"],
            "runtime_deps": ["libssl1.0.0", "python3-dbus", "gnome-keyring"],
            "after_install": 'packaging/postinst.sh',
            "after_remove": 'packaging/postuninst.sh',
            "output_folder": output_dir,
            "output_script": True
        },
        "geolocate-test-generate-pkg-from-git-setup-nocompile": {
            "app": 'geolocate',
            "version": '1.4.1',
            "source": git(
                uri='https://github.com/dante-signal31/geolocate',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "compile_python": False,
            # "python_version": '3.4.4',
            # Lets suppose custom python package is already installed and its root
            # folder is '/root/custom_python'.
            "python_basedir": '/root/custom_python',
            "fpm_args": FPM_ARGS_GEOLOCATE,
            "requirements_path": '/REQUIREMENTS.txt',
            "build_deps": ["python3", "base-devel", "openssl",
                           "pkg-config", "dbus-glib", "gnome-keyring",
                           "libffi"],
            "runtime_deps": ["openssl", "python-dbus", "gnome-keyring"],
            "after_install": 'packaging/postinst.sh',
            "after_remove": 'packaging/postuninst.sh',
            "output_folder": output_dir,
            "output_script": True
        },
        "jtrouble-test-generate-package-from-git-nosetup-compile": {
            "app": 'jtrouble',
            "version": '1.0.0',
            "source": git(
                uri='https://github.com/objectified/jtrouble',
                branch='master'
            ),
            "profile": profile_name,
            "package_install_root": "/opt",
            "python_basedir": "/opt/python",
            "compile_python": True,
            "python_version": '3.4.4',
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-package-from-git-setup-compile": {
            "app": 'vdist',
            "version": '1.1.0',
            "source": git(
                uri='https://github.com/dante-signal31/vdist',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "compile_python": True,
            "python_version": '3.5.3',
            "fpm_args": FPM_ARGS_VDIST,
            "requirements_path": '/REQUIREMENTS.txt',
            "runtime_deps": ["openssl", "docker-ce"],
            "after_install": 'packaging/postinst.sh',
            "after_remove": 'packaging/postuninst.sh',
            "output_folder": output_dir,
            "output_script": True
        },
        "vdist-test-generate-from-git": {
            "app": app_name,
            "version": '1.0',
            "source": git(
                uri='https://github.com/dante-signal31/vdist',
                branch='vdist_tests'
            ),
            "profile": profile_name,
            "output_folder": output_dir,
            "output_script": True
        }
    }
    return builder_configurations[app_name]


@pytest.mark.deb
@pytest.mark.generate_from_git
def test_generate_deb_from_git():
    _generate_package_from_git("ubuntu-lts",
                               "vdist-test-generate-from-git",
                               _generate_deb)


def _generate_package_from_git(distro,
                               package_name,
                               packager_function):
    with temporary_directory() as output_dir:
        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     "",
                                                     output_dir)
        _ = packager_function(builder_parameters)


@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_git
def test_generate_rpm_from_git_centos():
    _generate_package_from_git("centos",
                               "vdist-test-generate-from-git",
                               _generate_rpm)


@pytest.mark.rpm
@pytest.mark.centos7
@pytest.mark.generate_from_git
def test_generate_rpm_from_git_centos7():
    _generate_package_from_git("centos7",
                               "vdist-test-generate-from-git",
                               _generate_rpm)


@pytest.mark.pkg
@pytest.mark.generate_from_git
def test_generate_pkg_from_git():
    _generate_package_from_git("archlinux",
                               "vdist-test-generate-from-git",
                               _generate_pkg)


def test_output_script():
    with temporary_directory() as output_dir:
        ubuntu_argparsed_arguments_output_script = test_console.UBUNTU_ARGPARSED_ARGUMENTS.copy()
        ubuntu_argparsed_arguments_output_script["output_script"] = True
        ubuntu_argparsed_arguments_output_script["output_folder"] = output_dir
        _configuration = configuration.Configuration(ubuntu_argparsed_arguments_output_script)
        builder.build_package(_configuration)
        copied_script_path = _get_copied_script_path(_configuration)
        assert os.path.isfile(copied_script_path)


def _get_copied_script_path(_configuration):
    script_file_name = builder._get_script_output_filename(_configuration)
    script_output_folder = _configuration.output_folder
    copied_script_path = os.path.join(script_output_folder, script_file_name)
    return copied_script_path


# Scenarios to test:
# 1.- Project containing a setup.py and compiles Python -> only package the
#     whole Python basedir.
# 2.- Project not containing a setup.py and compiles Python -> package both the
#     project dir and the Python basedir.
# 3.- Project containing a setup.py and using a prebuilt Python package (e.g.
#     not compiling) -> package the custom Python basedir only
# 4.- Project not containing a setup.py and using a prebuilt Python package ->
#     package both the project dir and the Python basedir
# More info at:
#   https://github.com/dante-signal31/vdist/pull/7#issuecomment-177818848

# Scenario 1 - Project containing a setup.py and compiles Python -> only package
# the whole Python basedir.
@pytest.mark.deb
@pytest.mark.generate_from_git_setup_compile
def test_generate_deb_from_git_setup_compile():
    _generate_package_from_git_setup_compile("ubuntu-lts",
                                             "vdist-test-generate-package-from-git-setup-compile",
                                             _generate_deb,
                                             DEB_COMPILE_FILTER,
                                             ["./opt/vdist"],
                                             "./opt/vdist/bin/vdist")


@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_git_setup_compile
def test_generate_rpm_from_git_setup_compile_centos():
    _generate_package_from_git_setup_compile("centos",
                                             "vdist-test-generate-package-from-git-setup-compile",
                                             _generate_rpm,
                                             RPM_COMPILE_FILTER,
                                             ["/opt/vdist"],
                                             "/opt/vdist/bin/vdist")


@pytest.mark.rpm
@pytest.mark.centos7
@pytest.mark.generate_from_git_setup_compile
def test_generate_rpm_from_git_setup_compile_centos7():
    _generate_package_from_git_setup_compile("centos7",
                                             "vdist-test-generate-package-from-git-setup-compile",
                                             _generate_rpm,
                                             RPM_COMPILE_FILTER,
                                             ["/opt/vdist"],
                                             "/opt/vdist/bin/vdist")


@pytest.mark.pkg
@pytest.mark.generate_from_git_setup_compile
def test_generate_pkg_from_git_setup_compile():
    _generate_package_from_git_setup_compile("archlinux",
                                             "vdist-test-generate-package-from-git-setup-compile",
                                             _generate_pkg,
                                             PKG_COMPILE_FILTER,
                                             ["/opt", "/opt/vdist"],
                                             "/opt/vdist/bin/vdist")


# TODO: This function code is almost identical to the one in _generate_package_from_git_nosetup_nocompile. Try to resolve redundancy.
def _generate_package_from_git_setup_compile(distro,
                                             package_name,
                                             packager_function,
                                             compile_filter,
                                             correct_folders,
                                             launcher_path):
    with temporary_directory() as output_dir:
        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     "",
                                                     output_dir)
        target_file = packager_function(builder_parameters)
        file_list_purged = _get_purged_file_list(target_file,
                                                 compile_filter)
        # At this point only a folder should remain if everything is correct.
        assert all((True if any(folder in file_entry for folder in correct_folders)
                    else False
                    for file_entry in file_list_purged))
        # Launcher should be in bin folder too.
        assert launcher_path in file_list_purged



# Scenario 2.- Project not containing a setup.py and compiles Python -> package
# both the project dir and the Python basedir
@pytest.mark.deb
@pytest.mark.generate_from_git_nosetup_compile
def test_generate_deb_from_git_nosetup_compile():
    _generate_package_from_git_nosetup_compile("ubuntu-lts",
                                               "jtrouble-test-generate-package-from-git-nosetup-compile",
                                               _generate_deb,
                                               DEB_COMPILE_FILTER,
                                               ["./opt/jtrouble", "./opt/python"])


@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_git_nosetup_compile
def test_generate_rpm_from_git_nosetup_compile_centos():
    _generate_package_from_git_nosetup_compile("centos",
                                               "jtrouble-test-generate-package-from-git-nosetup-compile",
                                               _generate_rpm,
                                               RPM_COMPILE_FILTER,
                                               ["/opt/jtrouble", "/opt/python"])

@pytest.mark.rpm
@pytest.mark.centos7
@pytest.mark.generate_from_git_nosetup_compile
def test_generate_rpm_from_git_nosetup_compile_centos7():
    _generate_package_from_git_nosetup_compile("centos7",
                                               "jtrouble-test-generate-package-from-git-nosetup-compile",
                                               _generate_rpm,
                                               RPM_COMPILE_FILTER,
                                               ["/opt/jtrouble", "/opt/python"])


@pytest.mark.pkg
@pytest.mark.generate_from_git_nosetup_compile
def test_generate_pkg_from_git_nosetup_compile():
    _generate_package_from_git_nosetup_compile("archlinux",
                                               "jtrouble-test-generate-package-from-git-nosetup-compile",
                                               _generate_pkg,
                                               PKG_COMPILE_FILTER,
                                               ["/opt", "/opt/jtrouble", "/opt/python"])


## TODO: This function code is almost identical to the one in _generate_package_from_git_nosetup_nocompile. Try to resolve redundancy.
def _generate_package_from_git_nosetup_compile(distro,
                                               package_name,
                                               packager_function,
                                               compile_filter,
                                               correct_folders):
    with temporary_directory() as output_dir:
        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     "",
                                                     output_dir)
        target_file = packager_function(builder_parameters)
        file_list_purged = _get_purged_file_list(target_file,
                                                 compile_filter)
        # At this point only a folder should remain if everything is correct.
        assert all((True if any(folder in file_entry for folder in correct_folders)
                    else False
                    for file_entry in file_list_purged))
        # At this point only two folders should remain if everything is correct:
        # application folder and compiled interpreter folder: ["./opt/jtrouble", "./opt/python"]
        assert all((True if any(folder in file_entry for folder in correct_folders)
                    else False
                    for file_entry in file_list_purged))
        assert any(correct_folders[0] in file_entry
                   for file_entry in file_list_purged)
        assert any(correct_folders[1] in file_entry
                   for file_entry in file_list_purged)


# Scenario 3 - Project containing a setup.py and using a prebuilt Python package
# (e.g. not compiling) -> package the custom Python basedir only.
@pytest.mark.deb
@pytest.mark.generate_from_git_setup_nocompile
def test_generate_deb_from_git_setup_nocompile():
    _generate_package_from_git_setup_nocompile("ubuntu-lts-custom",
                                               "geolocate-test-generate-deb-from-git-setup-nocompile",
                                               _generate_deb,
                                               DEB_NOCOMPILE_FILTER,
                                               ["./root/custom_python"],
                                               "./root/custom_python/bin/python3.7",
                                               "./root/custom_python/bin/geolocate")

@pytest.mark.pkg
@pytest.mark.generate_from_git_setup_nocompile
def test_generate_pkg_from_git_setup_nocompile():
    _generate_package_from_git_setup_nocompile("archlinux-custom",
                                               "geolocate-test-generate-pkg-from-git-setup-nocompile",
                                               _generate_pkg,
                                               PKG_COMPILE_FILTER,
                                               ["/root/", "/root/custom_python"],
                                               "/root/custom_python/bin/python3.7",
                                               "/root/custom_python/bin/geolocate")


# TODO: These tests fails <<<<<<<<<<<<<
# WARNING: Something wrong happens with "nocompile" tests in centos7 and 6.
# I don't know why fpm call corrupts some lib in the linux container so
# further cp command fails. This does not happen in debian even
# when fpm commands are the same. Any help with this issue will be welcome.
# @pytest.mark.rpm
# @pytest.mark.centos
# @pytest.mark.generate_from_git_setup_nocompile
# def test_generate_rpm_from_git_setup_nocompile_centos():
#     _generate_package_from_git_setup_nocompile("centos-custom",
#                                                "geolocate-test_generate_rpm_from_git_setup_nocompile_centos",
#                                                _generate_rpm,
#                                                [],
#                                                ["/usr"],
#                                                "/root/custom_python/bin/python3",
#                                                "/root/custom_python/bin/geolocate")
#
# @pytest.mark.rpm
# @pytest.mark.centos7
# @pytest.mark.generate_from_git_setup_nocompile
# def test_generate_rpm_from_git_setup_nocompile_centos7():
#     _generate_package_from_git_setup_nocompile("centos7-custom",
#                                               "geolocate-test_generate_rpm_from_git_setup_nocompile_centos",
#                                               _generate_rpm,
#                                               [],
#                                               ["/usr"],
#                                               "/root/custom_python/bin/python3",
#                                               "/root/custom_python/bin/geolocate")


## TODO: This function code is almost identical to the one in _generate_package_from_git_nosetup_nocompile. Try to resolve redundancy.
def _generate_package_from_git_setup_nocompile(distro,
                                               package_name,
                                               packager_function,
                                               compile_filter,
                                               correct_folders,
                                               python_interpreter,
                                               geolocate_launcher):
    with temporary_directory() as output_dir:
        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     "",
                                                     output_dir)
        target_file = packager_function(builder_parameters)
        file_list_purged = _get_purged_file_list(target_file,
                                                 compile_filter)
        # At this point only a folder should remain if everything is correct.
        assert all((True if any(folder in file_entry for folder in correct_folders)
                    else False
                    for file_entry in file_list_purged))
        # If python basedir was properly packaged then /root/custom/bin/python should be
        # there.
        assert python_interpreter in file_list_purged
        # If application was properly packaged then launcher should be in bin folder
        # too.
        assert geolocate_launcher in file_list_purged

# Scenario 4.- Project not containing a setup.py and using a prebuilt Python
# package -> package both the project dir and the Python basedir
@pytest.mark.deb
@pytest.mark.generate_from_git_nosetup_nocompile
def test_generate_deb_from_git_nosetup_nocompile():
    _generate_package_from_git_nosetup_nocompile("ubuntu-lts-custom",
                                                 "jtrouble_nosetup_nocompile",
                                                 _generate_deb,
                                                 DEB_NOCOMPILE_FILTER,
                                                 ["./opt/jtrouble", "./usr", "./root/custom_python"],
                                                 "./root/custom_python/bin/python3.7")


@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_git_nosetup_nocompile
def test_generate_rpm_from_git_nosetup_nocompile_centos():
    _generate_rpm_from_git_nosetup_nocompile("centos-custom")


# TODO: This test fails <<<<<<<<<<<<<
# WARNING: Something wrong happens with "nocompile" tests in centos7.
# I don't know why fpm call corrupts some lib in the linux container so
# further cp command fails. This does not happen in centos or debian even
# when fpm commands are the same. Any help with this issue will be welcome.
# def test_generate_rpm_from_git_nosetup_nocompile_centos7():
#     _generate_rpm_from_git_nosetup_nocompile("centos7-custom")


def _generate_rpm_from_git_nosetup_nocompile(centos_version):
    _generate_package_from_git_nosetup_nocompile(centos_version,
                                                 "jtrouble_nosetup_nocompile",
                                                 _generate_rpm,
                                                 RPM_COMPILE_FILTER,
                                                 ["/opt/jtrouble", "/root/custom_python"],
                                                 "/root/custom_python/bin/python3")


@pytest.mark.pkg
@pytest.mark.generate_from_git_nosetup_nocompile
def test_generate_pkg_from_git_nosetup_nocompile():
    _generate_package_from_git_nosetup_nocompile("archlinux-custom",
                                                 "jtrouble_nosetup_nocompile",
                                                 _generate_pkg,
                                                 PKG_COMPILE_FILTER,
                                                 ["/root", "/opt", "/opt/jtrouble", "/root/custom_python"],
                                                 "/root/custom_python/bin/python3")


def _generate_package_from_git_nosetup_nocompile(distro,
                                                 package_name,
                                                 packager_function,
                                                 compile_filter,
                                                 correct_folders,
                                                 python_interpreter):
    with temporary_directory() as output_dir:
        builder_parameters =  _get_builder_parameters(package_name,
                                                      distro,
                                                      "",
                                                      output_dir)
        target_file = packager_function(builder_parameters)
        purged_file_list = _get_purged_file_list(target_file,
                                                 compile_filter)
        # At this point only two folders should remain if everything is correct:
        # application folder and python basedir folder.
        assert all((True if any(folder in file_entry for folder in correct_folders)
                    else False
                    for file_entry in purged_file_list))
        # If python basedir was properly packaged then python_interpreter path should be
        # there."
        assert python_interpreter in purged_file_list


@pytest.mark.deb
@pytest.mark.generate_from_git_suffixed
def test_generate_deb_from_git_suffixed():
    _generate_package_from_git_suffixed("ubuntu-lts",
                                        "vdist-test-generate-deb-from-git-suffixed",
                                        _generate_deb)

@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_git_suffixed
def test_generate_rpm_from_git_suffixed_centos():
    _generate_package_from_git_suffixed("centos",
                                        "vdist-test-generate-rpm-from-git-suffixed",
                                        _generate_rpm)


@pytest.mark.rpm
@pytest.mark.centos7
@pytest.mark.generate_from_git_suffixed
def test_generate_rpm_from_git_suffixed_centos7():
    _generate_package_from_git_suffixed("centos7",
                                        "vdist-test-generate-rpm-from-git-suffixed",
                                        _generate_rpm)


@pytest.mark.pkg
@pytest.mark.generate_from_git_suffixed
def test_generate_pkg_from_git_suffixed():
    _generate_package_from_git_suffixed("archlinux",
                                        "vdist-test-generate-pkg-from-git-suffixed",
                                        _generate_pkg)


def _generate_package_from_git_suffixed(distro, package_name, packager_function):
    with temporary_directory() as output_dir:
        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     "",
                                                     output_dir)
        _ = packager_function(builder_parameters)


@pytest.mark.deb
@pytest.mark.generate_from_git_directory
def test_generate_deb_from_git_directory():
    _generate_package_from_git_directory("ubuntu-lts",
                                         "vdist-test-generate-deb-from-git-dir",
                                         _generate_deb)


@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_git_directory
def test_generate_rpm_from_git_directory_centos():
    _generate_package_from_git_directory("centos",
                                         "vdist-test-generate-rpm-from-git-dir",
                                         _generate_rpm)


@pytest.mark.rpm
@pytest.mark.centos7
@pytest.mark.generate_from_git_directory
def test_generate_rpm_from_git_directory_centos7():
    _generate_package_from_git_directory("centos7",
                                         "vdist-test-generate-rpm-from-git-dir",
                                         _generate_rpm)


@pytest.mark.pkg
@pytest.mark.generate_from_git_directory
def test_generate_pkg_from_git_directory():
    _generate_package_from_git_directory("archlinux",
                                         "vdist-test-generate-pkg-from-git-dir",
                                         _generate_pkg)


def _generate_package_from_git_directory(distro, package_name, packager_function):
    with temporary_directory() as temp_dir, temporary_directory() as output_dir:
        git_p = subprocess.Popen(
            ['git', 'clone',
             'https://github.com/dante-signal31/vdist',
             temp_dir])
        git_p.communicate()

        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     temp_dir,
                                                     output_dir)
        _ = packager_function(builder_parameters)


@pytest.mark.deb
@pytest.mark.generate_from_directory
def test_generate_deb_from_directory():
    _generate_package_from_directory("ubuntu-lts",
                                     "vdist-test-generate-deb-from-dir",
                                     _generate_deb)


@pytest.mark.pkg
@pytest.mark.generate_from_directory
def test_generate_pkg_from_directory():
    _generate_package_from_directory("archlinux",
                                     "vdist-test-generate-pkg-from-dir",
                                     _generate_pkg)


@pytest.mark.rpm
@pytest.mark.centos
@pytest.mark.generate_from_directory
def test_generate_rpm_from_directory_centos():
    _generate_package_from_directory("centos",
                                     "vdist-test-generate-rpm-from-dir",
                                     _generate_rpm)


@pytest.mark.rpm
@pytest.mark.centos7
@pytest.mark.generate_from_directory
def test_generate_rpm_from_directory_centos7():
    _generate_package_from_directory("centos7",
                                     "vdist-test-generate-rpm-from-dir",
                                     _generate_rpm)


def _generate_package_from_directory(distro, package_name, packager_function):
    with temporary_directory() as temp_dir, temporary_directory() as output_dir:
        os.chdir(temp_dir)
        _populate_directory(temp_dir)
        builder_parameters = _get_builder_parameters(package_name,
                                                     distro,
                                                     temp_dir,
                                                     output_dir)
        _ = packager_function(builder_parameters)


def _populate_directory(temp_dir):
    ci_tools.run_console_command("git clone {} {}".format(VDIST_GITHUB_REPOSITORY,
                                                          temp_dir))
    ci_tools.run_console_command("git checkout {}".format(VDIST_TEST_BRANCH))


@pytest.mark.test_launcher
def test_generate_packages_from_configuration_file():
    configuration_file_name = "test_build.cnf"
    files_to_test = ["vdist_1.1.0_amd64.deb"]
    with temporary_directory() as temp_dir:
        configuration_path_name = os.path.join(temp_dir,
                                               configuration_file_name)
        os.chdir(temp_dir)
        with open(configuration_path_name, "w") as configuration_file:
            configuration_file.write(TEST_CONFIGURATION_FILE)
        console_arguments = console_parser.parse_arguments(["batch", configuration_path_name])
        configurations = launcher._get_build_configurations(console_arguments)
        launcher.run_builds(configurations)
        for file in files_to_test:
            file_pathname = os.path.join(temp_dir, "package_dist/", file)
            assert os.path.isfile(file_pathname)
            assert os.path.getsize(file_pathname) > 0
