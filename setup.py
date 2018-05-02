from setuptools import setup, find_packages
import ci_scripts.ci_tools as tools

VDIST_PACKAGES_CONFIG = "packaging/vdist_build.cnf"

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
    packages=find_packages(exclude=["tests", "integration-tests",
                                    "ci_scripts", "examples", "docs"]),
    install_requires=['jinja2==2.7.3', 'docker==3.2.1'],
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
