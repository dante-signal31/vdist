# ubuntu:latest tag points to latest LTS release. If you want the really latest
# version, you should use ubuntu:rolling.
FROM ubuntu:latest
LABEL maintainer="dante-signal31 (dante.signal31@gmail.com)"
LABEL description="Image to be used by vdist to package python applications into ubuntu deb packages."
# Abort on error.
RUN set -e
# Sometimes deb-src repositories comes disabled by default, we're activating it
# to use them for apt-get build-dep.
RUN sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list
# tzdata breaks automatized building because it asks user input. We must set it as
# unnattended.
# (See: https://stackoverflow.com/questions/44331836/apt-get-install-tzdata-noninteractive)
RUN apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y tzdata
# Install build tools.
RUN apt-get install ruby-dev build-essential git python-virtualenv curl libssl-dev libsqlite3-dev libgdbm-dev libreadline-dev libbz2-dev libncurses5-dev tk-dev python3 python3-pip libffi-dev -y
# Preload useful dependencies to compile python distributions.
RUN apt-get build-dep python python3 -y
# FPM installation to bundle app built directories into a system package file.
RUN gem install fpm