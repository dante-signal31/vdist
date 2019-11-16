FROM dantesignal31/vdist-aux:centos7
LABEL maintainer="dante-signal31 (dante.signal31@gmail.com)"
LABEL description="Don't use this image. It's only for vdist testing."

# Abort on error.
RUN set -e

# Download and compile what is going to be the Python we are going to use
# as our "custom" portable python environment.
ARG PYTHON_VERSION=3.7.5
ARG PYTHON_BASEDIR=/root/custom_python
RUN mkdir -p $PYTHON_BASEDIR
RUN yum -y --nogpgcheck update && \
    # Since Python 3.7 you need libffi to compile it.
    yum -y install libffi-devel && \
    cd /var/tmp && \
    curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar xzvf Python-$PYTHON_VERSION.tgz && \
    cd Python-$PYTHON_VERSION && \
    ./configure --prefix=$PYTHON_BASEDIR --with-ensurepip=install && \
    make && make install