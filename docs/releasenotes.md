## Release notes
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