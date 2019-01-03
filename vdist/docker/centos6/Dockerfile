FROM centos:centos6
MAINTAINER dante-signal31 (dante.signal31@gmail.com)
# Abort on error.
RUN set -e
# Install build tools.
RUN yum -y update
RUN yum groupinstall -y "Development Tools"
RUN yum install -y ruby-devel curl libyaml-devel which tar rpm-build rubygems git python-setuptools zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel gcc gcc-c++ libffi-devel
RUN yum install -y yum-utils
# Python 3 RPM installation to get basic support in that Python version.
# Idea taken from: http://stackoverflow.com/questions/8087184/problems-installing-python3-on-rhel
RUN yum install -y https://centos6.iuscommunity.org/ius-release.rpm
RUN yum install -y python35u python35u-pip
RUN ln -s /usr/bin/python3.5 /usr/bin/python3
RUN ln -s /usr/bin/pip3.5 /usr/bin/pip3
# Preload useful dependencies to compile python distributions.
RUN yum-builddep python27 python35u -y
# FPM installation to bundle app built directories into a system package file.
# Latest fpm fails to install in Centos 6.
#
# gem install fpm
#
# Applied workaround from:
#   https://github.com/jordansissel/fpm/issues/1192
#
RUN gem install fpm --no-ri --no-rdoc || gem install fpm --no-ri --no-rdoc --version 1.4.0