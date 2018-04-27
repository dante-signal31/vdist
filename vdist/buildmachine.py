from __future__ import absolute_import

import functools
import itertools
import logging
import os

import docker

import vdist.defaults as defaults


def print_output(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        # This is a method decorator.
        self = args[0]
        result = function(*args, **kwargs)
        for line in result.output:
            self.logger.info(line.decode("utf8"))
        return result
    return wrapper


class BuildMachine(object):

    def __init__(self, machine_logs=True, image=None):
        self.logger = logging.getLogger('BuildMachine')
        # self.machine_logs = machine_logs
        self.image = image
        self.container = None
        self.docker_client = docker.from_env()

    @staticmethod
    def _binds_to_shell_volumes(binds):
        volumes = {k: {'bind': v, 'mode': 'rw'} for k, v in binds.items()}
        return volumes

    def launch(self, build_dir, extra_binds=None):
        binds = {build_dir: defaults.SHARED_DIR}
        if extra_binds:
            binds = list(itertools.chain(binds.items(), extra_binds.items()))
        path_to_command = os.path.join(
            defaults.SHARED_DIR,
            defaults.SCRATCH_DIR,
            defaults.SCRATCH_BUILDSCRIPT_NAME
        )
        self.container = self._start_container(binds)
        self._run_command_on_container(path_to_command)

    @print_output
    def _run_command_on_container(self, path_to_command):
        output = self.container.exec_run(path_to_command, stream=True)
        return output

    def _start_container(self, binds):
        self.logger.info('Starting container: %s' % self.image)
        container = self.docker_client.containers.run(image=self.image, detach=True, command="bash", tty=True,
                                                      stdin_open=True, volumes=self._binds_to_shell_volumes(binds))
        return container

    def shutdown(self):
        self._stop_container()
        self._remove_container()

    def _remove_container(self):
        self.logger.info('Removing container: %s' % self.container.id)
        self.container.remove(force=True)

    def _stop_container(self):
        self.logger.info('Stopping container: %s' % self.container.id)
        self.container.stop()
