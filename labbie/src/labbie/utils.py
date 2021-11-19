import atexit
import dataclasses
import os
import pathlib
import sys

import loguru

logger = loguru.logger


def root_dir():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        # .../root/bin/labbie/Labbie.exe
        return pathlib.Path(sys.executable).parent.parent.parent
    else:
        # The application is not frozen
        # .../root/labbie/src/labbie/utils.py
        return pathlib.Path(__file__).parent.parent.parent.parent


def labbie_dir():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        # .../labbie/Labbie.exe
        return pathlib.Path(sys.executable).parent
    else:
        # The application is not frozen
        # .../labbie/src/labbie/utils.py
        return pathlib.Path(__file__).parent.parent.parent


def logs_dir():
    return root_dir() / 'logs'


def assets_dir():
    return labbie_dir() / 'assets'


def bin_dir():
    return root_dir() / 'bin'


def default_config_dir():
    return root_dir() / 'config'


def default_data_dir():
    return root_dir() / 'data'


def update_path():
    if getattr(sys, 'frozen', False):
        sys.path.append(str(root_dir() / 'lib'))


def relaunch(debug, exit_fn=None):
    cmd = []
    if sys.argv[0] == 'labbie':
        from labbie import __main__ as main
        cmd.append(main.__file__)
    else:
        cmd.append(f'"{sys.argv[0]}"')
    if debug:
        cmd.append('--debug')
    if not getattr(sys, 'frozen', False):
        cmd.insert(0, f'"{sys.executable}"')

    logger.info(f'{sys.argv=}')
    logger.info(f'{cmd=}')
    atexit.register(os.execv, sys.executable, cmd)
    if exit_fn:
        exit_fn()
    else:
        sys.exit(0)


def make_slotted_dataclass(cls):
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dataclasses.fields(cls))
    cls_dict['__slots__'] = field_names
    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)
    # Remove __dict__ itself.
    cls_dict.pop('__dict__', None)
    # And finally create the class.
    qualname = getattr(cls, '__qualname__', None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname
    return cls


class LogFilter:

    def __init__(self, level):
        self.level = level

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, val):
        self._level = logger.level(val).no

    def __call__(self, record):
        return record['level'].no >= self.level