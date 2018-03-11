# vdist

Welcome to the home of vdist, a tool that lets you create OS packages from your
Python applications in a clean and self contained manner.
It uses [virtualenv](https://virtualenv.pypa.io/en/latest/),
[Docker](https://www.docker.com/) and [fpm](https://github.com/jordansissel/fpm)
under the hood, and it uses [Jinja2](http://jinja.pocoo.org/docs/dev/) to render
its templates (shell scripts) for each individual target OS.

The source for vdist is available under the MIT license and can be found on
[Github](https://github.com/dante-signal31/vdist)

vdist is currently in beta stage, but it should work just fine. If you find any
issues, please report issues or submit pull requests via Github.

Here's a quickstart to give you an idea of how to use vdist, once you're set up.

Recommended way to use vdist is through it console launcher. First create a 
configuration file like this:

```ini
[DEFAULT]
app = yourapp
version = 1.0
source_git = https://github.com/you/%(app)s, master
compile_python = True
python_version = 3.4.4
requirements_path = ./requirements.txt
build_deps = package1, package2
runtime_deps = package3, package4
output_folder = ./generated_packages_folder
after_install = packaging/postinst.sh
after_remove = packaging/postuninst.sh

[Ubuntu-package]
profile = ubuntu-trusty

[Centos7-package]
profile = centos7
```

Let guess last file is called yourapp_vdist.cnf. Give that file to vdist 
launcher running next command:

```bash
$ vdist batch yourapp_vdist.cnf
```

Running the above would do this:

- set up a Docker container running Ubuntu Trusty Tahr

- install the OS packages listed in `build_deps`

- download and compile a python interpreter framework

- git clone the repository at https://github.com/you/yourapp

- checkout the branch 'master'

- install your application's dependencies from requirements.txt if found in the
checked out branch into compiled python framework

- if your application includes a setup.py then it is installed in compiled
python framework

- wrap the compiled python framework and your application files in a package
called `yourapp-1.0.deb` which includes a dependency on the OS packages listed
in `runtime_deps`

- repeat sequence setting up a Docker container running Centos 7.

- in the end you'll find generated packages for ubuntu and centos 7 in 
generated_packages_folder.

Read more about what vdist can do
[here](http://vdistdocs.readthedocs.io/en/latest/howtouse/)
