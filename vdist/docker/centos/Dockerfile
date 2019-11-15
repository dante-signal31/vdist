FROM centos:latest
MAINTAINER dante-signal31 (dante.signal31@gmail.com)
# Abort on error.
RUN set -e
# Install build tools.
RUN yum -y update && \
    # Install yum-utils to get config-manager for yum.
    yum install -y yum-utils && \
    # Libyaml-devel and other packages are not anymore if you don't enable PowerTools.
    yum config-manager --set-enabled PowerTools && \
    yum groupinstall -y "Development Tools" && \
    yum install -y ruby-devel curl libyaml-devel which tar rpm-build rubygems git zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel libpcap-devel xz-devel epel-release libffi-devel
# Python3 is not present by default at centos.
RUN yum install -y python3
# Preload useful dependencies to compile python distributions.
RUN yum-builddep -y python3
# FPM installation to bundle app built directories into a system package file.
RUN gem install fpm