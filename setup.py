from glob import glob
import os
from setuptools import setup, find_packages
from typing import List
import ci_scripts.ci_tools as tools

VDIST_PACKAGES_CONFIG = "packaging/vdist_build.cnf"


def find_folders_with_this_name(dir_name):
    """ Look for folder with given name, searching from current working dir.

    :param dir_name: Folder name to look for.
    :return: Relative path, from current working dir, where folder is.
    """
    for dir, dirs, files in os.walk('.'):
        if dir_name in dirs:
            yield os.path.relpath(os.path.join(dir, dir_name))


def find_man_pages():
    """ Look for every folder named "man", inside current working dir, and include
    its files relatives paths in a list suitable to be passed to a data_files
    setup.py parameter. This list will set those manpages to be installed to
    "share/man/man<section>" at target box.
    This code was inspired by a really interesting answer to:
    https://github.com/pypa/packaging-problems/issues/72#issuecomment-279162312

    :return: A list with tuples ("share/man/man<section>", local_relative_path_to_manpage)
    """
    data_files = []
    man_sections = {}
    for dir in find_folders_with_this_name('man'):
        for file in os.listdir(dir):
            # I wait man files to be gzipped and their name follow this pattern:
            # name.section.gz
            section = file.split('.')[-2]
            man_sections[section] = man_sections.get(section, []) + [os.path.join(dir, file)]
    for section in man_sections:
        data_files.append(('share/man/man{}'.format(section), man_sections[section]))
    return data_files


def find_info_pages():
    """ Look for every folder named "info", inside current working dir, and include
    its files relatives paths in a list suitable to be passed to a data_files
    setup.py parameter. This list will set those infopages to be installed to
    "share/info" at target box.
    This code was inspired by a really interesting answer to:
    https://github.com/pypa/packaging-problems/issues/72#issuecomment-279162312

    :return: A list with tuples ("share/info", local_relative_path_to_infopage)
    """
    data_files = []
    info_pages = {}
    for dir in find_folders_with_this_name('info'):
        for file in glob(os.path.join(dir, '*.info')):
            info_pages[dir] = info_pages.get(dir, []) + [file]
    for dir in info_pages:
        data_files.append(('share/info', info_pages[dir]))
    return data_files


setup(
    name='vdist',
    # Version is set in packaging/vdist_build.cnf and returned through
    # tools.get_current_version().
    version=tools.get_current_version(VDIST_PACKAGES_CONFIG),
    description='Create OS packages from Python '
                'projects using Docker containers',
    long_description='Create OS packages from Python '
                     'projects using Docker containers',
    author='objectified, dante-signal31',
    author_email='objectified@gmail.com, dante.signal31@gmail.com',
    license='MIT',
    url='https://github.com/dante-signal31/vdist',
    data_files=find_man_pages(),
    packages=find_packages(exclude=["tests", "integration-tests",
                                    "ci_scripts", "examples", "docs"]),
    install_requires=['jinja2==2.10.1', 'docker==3.2.1'],
    entry_points={'console_scripts': ['vdist=vdist.vdist_launcher:main', ], },
    package_data={'': ['internal_profiles.json', '*.sh']},
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
    keywords='python docker deployment packaging',
)
