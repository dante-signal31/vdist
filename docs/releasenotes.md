## Release notes
### 1.7.3 (2019/01/10)
- Manpage is now available. Just type "man vdist" and you'll get usage help.

### 1.5.0 (2018/11/05)
- Since Python 3.7 you need to add libffi-dev package to compile distribution. I 
added this installation in every profile.

### 1.4.9 (2018/05/06)
- Minor changes to improve the way exceptions are printed out in some
points of base code.

### 1.4.8 (2018/05/06)
- Travis build scripts habe been refactored to install vdist on Travis
from Pypi. That way I fixed some compatibility issues between docker
client library and docker server that is installed in Travis Ubuntu
version. Good news are that now Travis build step is some minutes 
shorter.
- Some build tasks were failing silently at Travis CI so I thought I was
packaging properly releases when I actually wasn't. So I've made some
changes to explicitely return error codes on exceptions to warn Travis
about error conditions. Hopefully this will make Travis fail the job and
stop it properly.
- Fixed a problem related with a docker client version mismatch.
- Removed some redundant code that caused a rare race condition at Travis-CI
build stage.
- Inner docker engine has been refactored to use docker API instead of console
commands. This way basecode is cleaner and easier to maintain.
- Since Python 2.7 is now longer a supported platform for vdist, all
inner python 2 code has been removed. That way code should be easier
to maintain.
- Codebase has been refactored to a more idiomatic Python 3.

### 1.3.1 (2012/04/27)
- Urgent fix. I've realized that packaging configuration had a wrong parameter,
so version that was being packaged was not from master branch but from
a wrong one.

### 1.3 (2018/04/21)
- Added multiprocessing support. Now builds are run parallely if run in
multicore machines. So, if you build for many targets you're going to
experience great performance improvement.
- This is the first release that removes Python 2 support. I want to
include some features to make code more maintainable but those are Python 3
only. Be aware that this only could affect you if you use vdist in
integration mode or from Pypi. If you use it from a DEB or RPM install
then you are safe because those packages include their own python framework
apart the one you use in your system.

### 1.2.12 (2018/03/10)
- Fixed bug that happened when building a package from a local folder tree. 
That bug made building fail when process tried to copy app folder tree to 
temp folder.

### 1.2.11 (2018/02/18)
- Building performance dramatically improved through using customized docker 
images with all dependencies already installed, so building time has been 
reduced by more than a half.
- Besides a new flag has been added to output used docker script in order 
to help with debugging if you are working in a custom profile.
- This is the first release that has been built using entirely automated 
testing, building and packaging with Travis CI. Thanks to this testing 
time has been greatly reduced and I won't waste time any longer building 
and packaging so hopefully I'm implementing features faster from now on.

### 1.1.0 (2017/04/09)
- Included six arguments to include scripts in your packages to be run
respectively after/before installation, removal, and upgrade.

### 1.0.0 (2017/02/25)
- Added console interface to launch vdist.