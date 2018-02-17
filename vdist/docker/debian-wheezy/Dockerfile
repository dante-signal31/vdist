FROM debian:wheezy
MAINTAINER dante-signal31 (dante.signal31@gmail.com)
# Abort on error.
RUN set -e
# Sometimes deb-src repositories comes disabled by default, we're activating it
# to use them for apt-get build-dep.
RUN printf "deb-src http://deb.debian.org/debian wheezy main \ndeb-src http://deb.debian.org/debian wheezy-updates main\ndeb-src http://security.debian.org wheezy/updates main\n" >> /etc/apt/sources.list
# Install build tools.
RUN apt-get update
RUN apt-get install ruby-dev build-essential git python-virtualenv curl libssl-dev libsqlite3-dev libgdbm-dev libreadline-dev libbz2-dev libncurses5-dev tk-dev python3 python3-pip -y
# Preload useful dependencies to compile python distributions.
RUN apt-get build-dep python python3 -y
# FPM installation to bundle app built directories into a system package file.
RUN gem install fpm