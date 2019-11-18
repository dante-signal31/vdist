## How to use
There are two ways to use vdist:

1. Using its [console launcher](#console-launcher)
2. [Create a small Python file](#integrating-vdist-in-a-python-script) that actually uses the vdist module

On both cases you are strongly advised to create a requirements.txt
('pip freeze > requirements.txt' inside a virtualenv should give you a good
start); nevertheless you are likely to already have one.

### Console launcher
Probably the simplest way to use vdist. When you install vdist Pypi package a
vdist executable is installed in your python distribution bin folder from which
you installed the package. If you have that folder in your PATH then you can
use vdist command directly, if not add that folder to path or call launcher
using its absolute path.

If you are going to use console launcher you only need to create a **configuration
file** to put all parameter for all packages you want to generate. An example of a
configuration file like that could be:

```ini
[DEFAULT]
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
profile = ubuntu-lts

[Centos-package]
profile = centos
```

Running vdist with last configuration file will place generated packages at path
you set in *output_folder* variable. If you don't use absolute path but a
relative one, then reference folder is the one where you are when vdist command
is called. **Always set *output_folder* variable**.

As you can see, there are three main **sections** in previous configuration: DEFAULT,
Ubuntu-package, Centos-package. You can name each section as you want but
DEFAULT that should always exists in your configurations because, as its name
suggest, it contains default values that will apply to all of your packages
unless one of the sections overrides any of the values. Write a section for
every package you want to create.

You can use **tags** in your configurations. In previous example ${app} tag
pastes the value you set in *app* variable. You can cross-reference values
from specific sections using tags with format *S{section:variable}*, but if you
you don't specify a section variable is fetched from current section and
probably from default one.

To parse your configuration python's [configparser](https://docs.python.org/3/library/configparser.html)
module is used. Be aware that [python 2's configparser](https://docs.python.org/2.7/library/configparser.html)
is somewhat limited so, if you use python 2 vdist version, you won't be able to
use cross-reference tags and you are going to need to change tags format because
python 2 argparser use tags with format: *%(variable)s* (pay attention to last "s"
it is not a typo). Because of that if you insist to use python 2 vdist version
your configuration file should look like the following:

```ini
[DEFAULT]
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
requirements_path = ./REQUIREMENTS.txt
runtime_deps = libssl1.0.0, dummy1.0.0
compile_python = True
python_version = 3.4.4
output_folder = ./vdist
after_install = packaging/postinst.sh
after_remove = packaging/postuninst.sh

[Ubuntu-package]
profile = ubuntu-lts

[Centos-package]
profile = centos
```

You can put your file whatever name and extension you want.

Once you have a configuration file you can launch vdist from your console using
**batch mode**:

```bash
$ vdist batch configuration_file
```

When launched vdist will create sequentially all packages configured in your
file.

Batch mode is the usual mode your are going to use through console but vdist
offers a **manual mode** too. That mode does not use a configuration file but
allows you to set parameters as command arguments:

```bash
$ vdist manual --app geolocate --version 1.3.0 --source_git https://github.com/dante-signal31/geolocate,master --profile ubuntu-lts --compile_python --python_version 3.4.4 --fpm_args '--maintainer dante.signal31@gmail.com -a native --url https://github.com/dante-signal31/geolocate --description "This program accepts any text and searchs inside every IP address." --license BSD-3 --category net' --requirements_path /REQUIREMENTS.txt --runtime_deps libssl1.0.0 dummy1.0.0 --output_folder ./dist --after_install = packaging/postinst.sh --after_remove = packaging/postuninst.sh
```

Pay attention to the point that `--fpm_args` argument is enclosed in single quotes.

Manual mode may be useful to dinamically set parameters through console scripts.

Whatever mode you use you can call console help anytime:

```bash
$ vdist --help
[...]

$ vdist batch --help
[...]

$ vdist manual --help
[...]
```

At ["Required arguments"](#required-arguments) and
["Optional arguments"](#optional-arguments) sections, below in this very
text, you can find a list of parameters you can set in your configuration file
or through console manual parameters.

### Integrating vdist in a python script
Sometimes you may need not to run vdist from console but integrating it in
another python application. You can do it too. In this section we are going
to explain how to use vdist modules programatically.

Here is a minimal example of how to use vdist to create an OS package of
"yourapp" for Ubuntu Trusty. Create a file called package.py, which would
contain the following code:

```python
import vdist.builder as builder
from vdist.configuration import Configuration
from vdist.source import git

builder_parameters = {
            "app": 'yourapp',
            "version": '1.0',
            "source": git(uri='https://github.com/you/yourapp',
                          branch='master'),
            "profile": 'ubuntu-lts',
        }

configuration = Configuration(builder_parameters)

builder.build_package(configuration)
```

Here is what it does: vdist will build an OS package called 'yourapp-1.0.deb'
from a Git repo located at https://github.com/you/yourapp, from branch 'master'
using the vdist profile 'ubuntu-lts' (more on vdist profiles later).
While doing so, it will download and compile a Python interpreter framework and
installs your application's dependencies
into that framework. The whole resulting python framework will be wrapped up in a
package, and is the end result of the build run.

At ["Required arguments"](#required-arguments) and
["Optional arguments"](#optional-arguments) sections, below in this very
text, you can find a list of parameters you can set to create your Configuration 
instance to be passed to build_package().

### Required arguments:
- `app` :: the name of the application to build; this should also equal the
project name in Git, and is used as the prefix for the filename of the
resulting package
- `version` :: the version of the application; this is used when building the
OS package both in the name and in its meta information
- `profile` :: the name of the profile to use for this specific build; its
value should be one of two things:
    * a vdist built-in profile (currently `centos`, `ubuntu-lts` and
    `debian-wheezy` are available, `centos7`, `ubuntu-trusty` are deprecated 
    and will be removed soon).
    * a custom profile that you create yourself; see
    [How to customize](http://vdistdocs.readthedocs.io/en/latest/howtocustomize/)
    for instructions
- `source` :: the argument that specifies how to get the source code to build
from; the available source types are:
    * `git(uri=uri, branch=branch)`: this source type attempts to git clone by
    using the supplied arguments
    * `directory(path=path)`: this source type uses a local directory to build
    the project from, and uses no versioning data
    * `git_directory(path=path, branch=branch)`: this source type uses a git
    checkout in a local directory to build the project from; it checks out the
    supplied branch before building

### Optional arguments:
- `name` :: the name of the build; this does not do anything in the build
process itself, but is used in e.g. logs; when omitted, the build name is a
sanitized combination of the `app`, `version` and `profile` arguments.
- `build_deps` :: a list of build time dependencies; these are the names of
the OS packages that need to be present on the build machine before setting
up and building the project.
- `runtime_deps` :: a list of run time dependencies; these names are given to
the resulting OS package as dependencies, so that they act as prerequisites
when installing the final OS package.
- `custom_filename` :: specifies a custom filename to use when generating
the OS package; within this filename, references to environment variables
may be used when put in between curly braces
(e.g. `foo-{ENV_VAR_ONE}-bar-{ENV_VAR_TWO}.deb`); this is useful when for
example your CI system passes values such as the build number and so on.
- `fpm_args` :: any extra arguments that are given to
[fpm](https://github.com/jordansissel/fpm) when the actual package is being
built.
- `pip_args` :: any extra arguments that are given to pip when your pip
requirements are being installed (a custom index url pointing to your private
PyPI repository for example).
- `package_install_root`:: Base directory were this package is going to be
installed in target system (defaults to '*python_basedir*').
- `package_tmp_root` :: Temporal folder used in docker container to build your
package (defaults to '*/tmp*').
- `working_dir` :: a subdirectory under your source tree that is to be regarded
as the base directory; if set, only this directory is packaged, and the pip
requirements are tried to be found here. This makes sense when you have a
source repository with multiple projects under it.
- `python_basedir` :: specifies one of two things: 1) where Python can be
found (your company might have a prepackaged Python already installed on your
custom docker container) 2) where vdist should install the compiled Python
distribution on your docker container. Read vdist's various [use cases](usecases.md)
to understand the nuance. Defaults to '*/opt*'.
- `compile_python` :: indicates whether Python should be fetched from
python.org, compiled and shipped for you; defaults to *True*. If not *True* then
'*python_basedir*' should point to a python distribution already installed in
docker container.
- `python_version` :: specifies two things: 1) if '*compile_python*' is *True*
then it means the exact python version that should be downloaded and compiled.
2) if '*compile_python*' is *False* then only mayor version number is considered
(currently 2 or 3) and latest available python distribution of that mayor
version is searched (in given '*python_basedir*' of your docker container) to be
used. Defaults to '*2.7.9*'.
- `requirements_path` :: the path to your pip requirements file, relative to
your project root; this defaults to `*/requirements.txt*`.
- `after_install` :: A script to include inside package to be run after package
installation. Given path should be given relative to the root of your source
project folder.
- `before_install` :: A script to include inside package to be run before package
installation. Given path should be given relative to the root of your source
project folder.
- `after_remove` :: A script to include inside package to be run after package
removal. Given path should be given relative to the root of your source
project folder.
- `before_remove` :: A script to include inside package to be run before package
removal. Given path should be given relative to the root of your source
project folder.
- `after_upgrade` :: A script to include inside package to be run after package
upgrade. Given path should be given relative to the root of your source
project folder.
- `before_upgrade` :: A script to include inside package to be run before package
upgrade. Given path should be given relative to the root of your source
project folder.

Here's another, more customized example.

```python
import os

from vdist.builder import Builder
from vdist.source import directory

# Instantiate the builder while passing it a custom location for
# your profile definitions
profiles_path = os.path.dirname(os.path.abspath(__file__))

builder = Builder(profiles_dir='%s/deploy/profiles' % profiles_path)

# Add CentOS build
builder.add_build(
    # Name of the build
    name='myproject :: centos build',

    # Name of the app (used for the package name)
    app='myproject',

    # The version; you might of course get this value from e.g. a file
    # or an environment variable set by your CI environment
    version='1.0',

    # Base the build on a directory; this would make sense when executing
    # vdist in the context of a CI environment
    source=directory(path='/home/ci/projects/myproject'),

    # Use the 'centos' profile
    profile='centos',

    # Do not compile Python during packaging, a custom Python interpreter is
    # already made available on the build machine
    compile_python=False,

    # The location of your custom Python interpreter as installed by an
    # OS package (usually from a private package repository) on your
    # docker container.
    python_basedir='/opt/yourcompany/python',
    # As python_version is not given, vdist is going to assume your custom
    # package is a Python 2 interpreter, so it will call 'python'. If your
    # package were a Python 3 interpreter then you should include a
    # python_version='3' in this configuration to make sure that vdist looks
    # for a 'python3' executable in 'python_basedir'.

    # Depend on an OS package called "yourcompany-python" which would contain
    # the Python interpreter; these are build dependencies, and are not
    # runtime dependencies. You docker container should be configured to reach
    # your private repository to get "yourcompany-python" package.
    build_deps=['yourcompany-python', 'gcc'],

    # Specify OS packages that should be installed when your application is
    # installed
    runtime_deps=['yourcompany-python', 'imagemagick', 'ffmpeg'],

    # Some extra arguments for fpm, in this case a postinstall script that
    # will run after your application will be installed (useful for e.g.
    # startup scripts, supervisor configs, etc.)
    fpm_args='--post-install deploy/centos7/postinstall.sh',

    # Extra arguments to use when your pip requirements file is being installed
    # by vdist; a URL to your private PyPI server, for example
    pip_args='--index-url https://pypi.yourcompany.com/simple/',

    # Find your pip requirements somewhere else instead of the project root
    requirements_path='deploy/requirements-prod.txt',
    
    # Specify a custom filename, including the values of environment variables
    # to build up the filename; these can be set by e.g. a CI system
    custom_filename='myapp-{GIT_TAG}-{CI_BUILD_NO}-{RELEASE_NAME}.deb'
)

builder.run_build()
```
You can read some examples with the main vdist [use cases](usecases.md) we have
identified. Additionally if you look in the
[vdist examples directory](https://github.com/dante-signal31/vdist/tree/master/examples),
you will find even more examples.

There are cases where you want to influence the way vdist behaves in your
environment. This can be done by passing additional parameters to the vdist
Builder constructor. Here's an example:

```
import os

from vdist.builder import Builder
from vdist.source import git

profiles_dir = os.path.join(os.path.dirname(__file__), 'myprofiles')

builder = Builder(
    profiles_dir=profiles_dir,
    machine_logs=False
)

builder.add_build(
    app='myapp',
    source=git(uri='https://github.com/foo/myproject', branch='myrelease'),
    version='1.0',
    profile='ubuntu-lts'
)

builder.run_build()
```

In the above example, two things are customized for this build run:

1. vdist looks at a different directory for finding your custom profiles

2. the logging of what happens on the Docker image is turned off
