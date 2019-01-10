FROM centos:centos7
LABEL maintainer="dante-signal31 (dante.signal31@gmail.com)"
LABEL description="Image to be used by vdist to package python applications into centos rpm packages."
# Abort on error.
RUN set -e
# Install build tools.
RUN yum -y update && \
    yum groupinstall -y "Development Tools" && \
    yum install -y ruby-devel curl libyaml-devel which tar rpm-build rubygems git python-setuptools zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel epel-release libffi-devel
# Python 3 RPM installation to get basic support in that Python version.
# Idea taken from: http://stackoverflow.com/questions/8087184/problems-installing-python3-on-rhel
# and: http://www.codeghar.com/blog/install-latest-python-on-centos-7.html
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python35u python35u-pip
RUN ln -s /usr/bin/python3.5 /usr/bin/python3 && \
    ln -s /usr/bin/pip3.5 /usr/bin/pip3
# Preload useful dependencies to compile python distributions.
RUN yum-builddep python python35u -y
# FPM installation to bundle app built directories into a system package file.
RUN gem install fpm