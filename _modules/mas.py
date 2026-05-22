import json
import logging
import shlex

import salt.utils.platform
import salt.utils.versions
from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)

__virtualname__ = "mas"


def __virtual__():
    """
    Only work on Mac OS
    """
    if salt.utils.platform.is_darwin():
        return __virtualname__
    return False


def _which():
    if exe := __salt__["cmd.run_stdout"]("command -v mas"):
        log.debug("Found mas at %s", exe)
        return exe
    if exe := __salt__["cmd.run_stdout"]("brew --prefix mas"):
        log.debug("Found mas at %s", exe)
        return exe
    raise CommandExecutionError("Could not find mas executable.")


def _mas(cmd, *args, jsonfmt=True):
    cmd = [_which(), cmd]
    if jsonfmt:
        cmd.append("--json")
    cmd.extend(args)
    res = __salt__["cmd.run_stdout"](shlex.join(cmd), raise_err=True)
    if jsonfmt:
        try:
            return json.loads(res)
        except json.JSONDecodeError:
            return [json.loads(line) for line in res.splitlines()]
    return res


def is_installed(name):
    """
    Inquire whether an app is installed.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.is_installed Telegram
        salt '*' mas.is_installed 747648890

    name
        The name or ID of the app to inquire about. Passing
        a name will look up the ID of the most relevant search result.

    """

    if _is_id(name):
        return int(name) in _list_installed()
    return name in _list_installed().values()


def is_outdated(name):
    """
    Check whether an app is outdated.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.is_outdated Telegram
        salt '*' mas.is_outdated 747648890

    name
        The name or ID of the app to check. Passing
        a name will look up the ID of the most relevant search result.

    """

    if not is_installed(name):
        raise CommandExecutionError(f"App '{name}' is not installed.")

    current = _get_current_version(name)
    latest = _get_latest_version(name)

    return salt.utils.versions.parse(current) < salt.utils.versions.parse(latest)


def install(name):
    """
    Install an app from the MacOS App Store.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.install Telegram
        salt '*' mas.install 747648890

    name
        The name or ID of the app to install. Passing
        a name will look up the ID of the most relevant search result.

    """

    if not _is_id(name):
        log.info("mas is installing first search result of '%s'", name)
        _mas("lucky", name, jsonfmt=False)
        return True
    _mas("install", str(name), jsonfmt=False)
    return True


def remove(name):
    """
    Remove an app.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.remove Telegram
        salt '*' mas.remove 747648890

    name
        The name or ID of the app to remove. Passing
        a name will look up the ID of the most relevant search result.

    """

    # NOTE: This issue has been fixed in v1.8.7, but might ask for privileges

    # https://github.com/mas-cli/mas/issues/313
    # requires root permissions to move to trash, but when running as root,
    # does not find the installed app. since mas only moves to trash, replicate
    # that in python

    # this part would fail in mas since it was running as root
    info = _lookup_local(name)
    if not info:
        raise CommandExecutionError(f"Could not find app '{name}'")
    appid, path = info["adamID"], info["path"]

    try:
        from ctypes import Structure, byref, c_char, c_char_p, cdll
        from ctypes.util import find_library

        Foundation = cdll.LoadLibrary(find_library("Foundation"))
        CoreServices = cdll.LoadLibrary(find_library("CoreServices"))
        Foundation.GetMacOSStatusCommentString.restype = c_char_p

        class Ref(Structure):
            _fields_ = [("hidden", c_char * 80)]

        def check(res):
            if res:
                msg = Foundation.GetMacOSStatusCommentString(res).decode("utf-8")
                raise CommandExecutionError(msg)

        def trash(path):
            if not isinstance(path, bytes):
                path = path.encode("utf-8")
            f = Ref()
            res = CoreServices.FSPathMakeRefWithOptions(path, 0x01, byref(f), None)
            check(res)
            res = CoreServices.FSMoveObjectToTrashSync(byref(f), None, 0)
            check(res)

        trash(path)
    except Exception:
        _mas("remove", appid)
    return True


def upgrade(name):
    """
    Upgrade an app.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.upgrade Telegram
        salt '*' mas.upgrade 747648890

    name
        The name or ID of the app to upgrade. Passing
        a name will look up the ID of the most relevant search result.

    """

    if not _is_id(name) and not (name := _get_local_id(name)):
        raise CommandExecutionError(f"Could not find installation of '{name}'.")

    _mas("upgrade", str(name))
    return True


def _get_current_version(name):
    appid = _get_local_id(name)
    installed = _list_installed(versions=True)
    return installed.get(appid)


def _get_latest_version(name):
    appid = _get_local_id(name)
    return _mas("info", str(appid))["version"]


def _list_installed(versions=False):
    res = _mas("list")
    if versions:
        return {app["adamID"]: app["version"] for app in res}
    return {app["adamID"]: app["name"] for app in res}


def _is_id(value):
    try:
        value = int(value)
    except ValueError:
        return False
    return True


def _lookup_local(name):
    isid = _is_id(name)
    for app in _mas("list"):
        if isid and app["adamID"] == int(name) or not isid and app["name"] == name:
            return app


def _get_local_id(name):
    if _is_id(name):
        return int(name)
    info = _lookup_local(name)
    if info:
        log.debug("mas found id of installed app '%s': %s", name, info["adamID"])
        return info["adamID"]
    return False
