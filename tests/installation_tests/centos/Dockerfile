FROM centos:centos7
LABEL maintainer="dante-signal31 (dante.signal31@gmail.com)"
LABEL description="Image to test installation of vdist rpm packages."
# Abort on error.
RUN set -e
# Install docker-ce.
RUN yum install -y yum-utils && \
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && \
    yum install -y docker-ce
# Configure vdist deb repo if we want to test installation downloading from there.
RUN wget https://bintray.com/dante-signal31/rpm/rpm -O bintray-dante-signal31-rpm.repo && \
    mv bintray-dante-signal31-rpm.repo /etc/yum.repos.d/ && \
    yum install -y yum-utils && \
# Refresh everything.
RUN yum -y update
