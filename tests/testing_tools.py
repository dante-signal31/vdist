from __future__ import print_function

import sys
import tempfile

# Python 2.x specific tools.
if sys.version_info[0] != 3:

    # Python 2.x lacks of tempfile.TemporaryDirectory context manager
    # so I must code my own context manager.
    # Code adapted from:
    #   http://stackoverflow.com/questions/19296146/tempfile-temporarydirectory-context-manager-in-python-2-7
    import os
    import warnings

    from tempfile import mkdtemp

    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        def __init__(self, suffix="", prefix="tmp", dir=None):
            self._closed = False
            self.name = None  # Handle mkdtemp raising an exception
            self.name = mkdtemp(suffix, prefix, dir)

        def __repr__(self):
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def __del__(self):
            # Issue a ResourceWarning if implicit cleanup needed
            self.cleanup(_warn=True)

        def _rmtree(self, path):
            # Essentially a stripped down version of shutil.rmtree.  We can't
            # use globals because they may be None'ed out at shutdown.
            for name in os.listdir(path):
                fullname = os.path.join(path, name)
                try:
                    isdir = os.path.isdir(fullname) and not os.path.islink(
                        fullname)
                except OSError:
                    isdir = False
                if isdir:
                    self._rmtree(fullname)
                else:
                    try:
                        os.remove(fullname)
                    except OSError:
                        pass
            try:
                os.rmdir(path)
            except OSError:
                pass

        def cleanup(self, _warn=False):
            if self.name and not self._closed:
                try:
                    self._rmtree(self.name)
                except (TypeError, AttributeError) as ex:
                    # Issue #10188: Emit a warning on stderr
                    # if the directory could not be cleaned
                    # up due to missing globals
                    if "None" not in str(ex):
                        raise
                    print(
                        "ERROR: {!r} while cleaning up {!r}".format(ex, self, ),
                        file=sys.stderr)
                    return
                self._closed = True
                if _warn:
                    warnings.warn("Implicitly cleaning up {!r}".format(self),
                                  ResourceWarning)


def get_temporary_directory_context_manager():
    if sys.version_info[0] == 3:
        temporary_directory = tempfile.TemporaryDirectory
    else:
        temporary_directory = TemporaryDirectory
    return temporary_directory
