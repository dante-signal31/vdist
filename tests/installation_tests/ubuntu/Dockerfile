FROM ubuntu
LABEL maintainer="dante-signal31 (dante.signal31@gmail.com)"
LABEL description="Image to test installation of vdist deb packages."
# Abort on error.
RUN set -e
# Sometimes deb-src repositories comes disabled by default, we're activating it
# to use them for apt-get build-dep.
RUN sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list && sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list
# Install vdist dependencies.
RUN apt-get update && \
    apt-get install apt-transport-https gnupg -y
# Configure vdist deb repo if we want to test installation downloading from there.
RUN echo "deb [trusted=yes] https://dl.bintray.com/dante-signal31/deb generic main" | tee -a /etc/apt/sources.list && \
    apt-key adv --keyserver pgp.mit.edu --recv-keys 379CE192D401AB61 && \
    apt-get --reinstall install ca-certificates -y
# Install docker-ce.
RUN apt-get install curl software-properties-common -y && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get install docker-ce -y
# Install manpage support.
RUN apt-get install man -y
# Refresh everything.
RUN apt-get update