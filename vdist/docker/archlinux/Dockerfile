FROM archlinux:latest
LABEL maintainer="dante-signal31 (dante.signal31@gmail.com)"
LABEL description="Image to be used by vdist to package python applications into archlinux pacman packages."
# Abort on error.
RUN set -e
# Install build tools.
RUN pacman -Syu --noconfirm && \
    pacman -S ruby base-devel openssl sqlite3 gdbm readline bzip2 ncurses tk libffi git python-virtualenv curl python python-pip --noconfirm
# FPM installation to bundle app built directories into a system package file.
RUN gem install fpm