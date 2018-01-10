from setuptools import setup, find_packages

# [TODO] ci_scripts and test is wrongly included in package. I have to fix it.
setup(
    name='vdist',
    version='1.2.1',
    description='Create OS packages from Python '
                'projects using Docker containers',
    long_description='Create OS packages from Python '
                     'projects using Docker containers',
    author='objectified, dante-signal31',
    author_email='objectified@gmail.com, dante.signal31@gmail.com',
    license='MIT',
    url='https://github.com/dante-signal31/vdist',
    packages=find_packages(),
    install_requires=['jinja2==2.7.3'],
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=False,
    keywords='python docker deployment packaging',
)
