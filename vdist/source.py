from typing import Dict


def git(uri: str=None, branch: str='master') -> Dict[str, str]:
    if uri.endswith('.git'):
        uri = uri[:-4]
    return dict(type='git', uri=uri, branch=branch)


def directory(path:str =None) -> Dict[str, str]:
    path = path.rstrip('/')
    return dict(type='directory', path=path)


def git_directory(path: str=None, branch: str='master') -> Dict[str, str]:
    path = path.rstrip('/')
    return dict(type='git_directory', path=path, branch=branch)
