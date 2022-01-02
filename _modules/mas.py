from salt.exceptions import CommandExecutionError
# import logging
import json

import salt.utils.platform

# log = logging.getLogger(__name__)
__virtualname__ = "mas"


def __virtual__():
    """
    Only work on Mac OS
    """
    if salt.utils.platform.is_darwin():
        return __virtualname__
    return False


def _which(user=None):
    if e := salt["cmd.run"]("command -v mas", runas=user):
        return e
    if salt.utils.platform.is_darwin():
        if p := salt["cmd.run"]("brew --prefix mas", runas=user):
            return p
    raise CommandExecutionError("Could not find pipx executable.")


def is_installed(name, user=None):
    if _is_id(name):
        return name in _list_installed(user).keys()
    return name in _list_installed(user).values()


def install(name, user=None):
    e = _which(user)

    if not _is_id(name):
        return __salt__['cmd.retcode']("{} lucky '{}'".format(e, name), runas=user)

    return __salt__['cmd.retcode']("{} install {}".format(e, name), runas=user)


def remove(name, user=None):
    e = _which(user)

    if not _is_id(name) and not (name := _get_local_id(name)):
        raise CommandExecutionError("Could not find installation of '{}'.".format(name))

    return __salt__['cmd.retcode']("{} uninstall {}".format(e, name), runas=user)


def upgrade(name, user=None):
    e = _which(user)

    if not _is_id(name) and not (name := _get_local_id(name)):
        raise CommandExecutionError("Could not find installation of '{}'.".format(name))

    return __salt__['cmd.retcode']("{} upgrade '{}'".format(e, name), runas=user)


def _list_installed(user=None):
    e = _which(user)
    ls = _parse_list(__salt__['cmd.run']("{} list".format(e), runas=user))
    return {x[0]: x[1] for x in ls}


def _is_id(value):
    try:
        value = int(value)
    except ValueError:
        return False
    return True


def _find_id(name, user=None):
    if _is_id(name):
        return name
    e = _which(user)
    ls = __salt__['cmd.run']("{} search '{}'".format(e, name))
    try:
        return _parse_list(ls)[0][0]
    except IndexError:
        return False


def _get_local_id(name, user=None):
    if _is_id(name):
        return name
    for i, appname in _list_installed().items():
        if appname == name:
            return i
    return False


def _parse_list(ls):
    parsed = []
    for x in ls.splitlines():
        x0, r = x.split(None, 1)
        r, x2 = r.rsplit(None, 1)
        x1 = r.strip()
        parsed.append((x0, x1, x2))
    return parsed
