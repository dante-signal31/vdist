import itertools
import logging
import os
from typing import Dict, Any
import docker

import vdist.defaults as defaults


class BuildMachine(object):

    def __init__(self, image: str=None):
        self.logger = logging.getLogger('BuildMachine')
        self.image = image
        self.container = None
        self.docker_client = docker.from_env(version="auto")

    @staticmethod
    def _binds_to_shell_volumes(binds: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        volumes = {k: {'bind': v, 'mode': 'rw'} for k, v in binds.items()}
        return volumes

    def launch(self, build_dir: str, extra_binds: Dict[str, str]=None) -> None:
        binds = {build_dir: defaults.SHARED_DIR}
        if extra_binds:
            binds = dict(itertools.chain(binds.items(), extra_binds.items()))
        path_to_command = os.path.join(
            defaults.SHARED_DIR,
            defaults.SCRATCH_DIR,
            defaults.SCRATCH_BUILDSCRIPT_NAME
        )
        self.container = self._start_container(binds)
        self._run_command_on_container(path_to_command)

    def _run_command_on_container(self, path_to_command: str) -> int:
        result = self.container.exec_run(path_to_command, stream=True)
        for line in result.output:
            self.logger.info(line.decode("utf8"))
        return result.exit_code

    # I've been unable to locate Container class in docker exported hierarchy. So I've set Any as return type.
    def _start_container(self, binds: Dict[str, str]) -> Any:
        self.logger.info(f'Starting container: {self.image}')
        container = self.docker_client.containers.run(image=self.image, detach=True, command="bash", tty=True,
                                                      stdin_open=True, volumes=self._binds_to_shell_volumes(binds))
        return container

    def shutdown(self) -> None:
        self._stop_container()
        self._remove_container()

    def _remove_container(self) -> None:
        self.logger.info(f'Removing container: {self.container.id}')
        self.container.remove(force=True)

    def _stop_container(self) -> None:
        self.logger.info(f'Stopping container: {self.container.id}')
        self.container.stop()
