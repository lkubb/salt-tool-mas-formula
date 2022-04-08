import re

from pkg_resources import packaging

import salt.utils.platform
from salt.exceptions import CommandExecutionError

__virtualname__ = "mas"


def __virtual__():
    """
    Only work on Mac OS
    """
    if salt.utils.platform.is_darwin():
        return __virtualname__
    return False


def _which(user=None):
    e = __salt__["cmd.run_stdout"]("command -v mas", runas=user)
    # if e := __salt__["cmd.run_stdout"]("command -v mas", runas=user):
    if e:
        __salt__["log.info"]("Found mas: '{}'".format(e))
        return e
    if salt.utils.platform.is_darwin():
        p = __salt__["cmd.run_stdout"]("brew --prefix mas", runas=user)
        # if p := __salt__["cmd.run_stdout"]("brew --prefix mas", runas=user):
        if p:
            __salt__["log.info"]("Found mas: '{}'".format(p))
            return p
    raise CommandExecutionError("Could not find mas executable.")


def is_installed(name, user=None):
    """
    Inquire whether an app is installed.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.is_installed Telegram
        salt '*' mas.is_installed "747648890"

    name
        The name or ID of the app to inquire about. Passing
        a name will look up the ID of the most relevant search result.
        If you want to be precise, pass the numeric ID as a string.
        This avoids implicit casting issues.

    user
        The username to inquire about the app for. Defaults to salt user.
    """

    if _is_id(name):
        return str(name) in list(_list_installed(user).keys())
    return name in list(_list_installed(user).values())


def is_outdated(name, user=None):
    """
    Check whether an app is outdated.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.is_outdated Telegram
        salt '*' mas.is_outdated "747648890"

    name
        The name or ID of the app to check. Passing
        a name will look up the ID of the most relevant search result.
        If you want to be precise, pass the numeric ID as a string.
        This avoids implicit casting issues.

    user
        The username to check the app for. Defaults to salt user.

    """

    if not is_installed(name, user):
        raise CommandExecutionError(
            "App '{}' is not installed for user '{}'.".format(name, user)
        )

    current = _get_current_version(name, user)
    latest = _get_latest_version(name, user)

    return packaging.version.parse(current) < packaging.version.parse(latest)


def install(name, user=None):
    """
    Install an app from the MacOS App Store.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.install Telegram
        salt '*' mas.install "747648890"

    name
        The name or ID of the app to install. Passing
        a name will look up the ID of the most relevant search result.
        If you want to be precise, pass the numeric ID as a string.
        This avoids implicit casting issues.

    user
        The username to install the app for. Defaults to salt user.

    """

    e = _which(user)

    if not _is_id(name):
        __salt__["log.info"](
            "mas is installing first search result of '{}'".format(name)
        )
        return not __salt__["cmd.retcode"]("{} lucky '{}'".format(e, name), runas=user)

    __salt__["log.info"]("mas is installing {}".format(name))

    # retcode returns shell-style retcode, need inverse
    return not __salt__["cmd.retcode"]("{} install {}".format(e, name), runas=user)


def remove(name, user=None):
    """
    Remove an app.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.remove Telegram
        salt '*' mas.remove "747648890"

    name
        The name or ID of the app to remove. Passing
        a name will look up the ID of the most relevant search result.
        If you want to be precise, pass the numeric ID as a string.
        This avoids implicit casting issues.

    user
        The username to remove the app for. Defaults to salt user.

    """

    # https://github.com/mas-cli/mas/issues/313
    # requires root permissions to move to trash, but when running as root,
    # does not find the installed app. since mas only moves to trash, replicate
    # that in python
    from ctypes import cdll, byref, Structure, c_char, c_char_p
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

    # this part would fail in mas since it was running as root
    appname = _get_local_name(name, user)

    if not appname:
        raise CommandExecutionError(
            "Could not find installed application '{}'.".format(name)
        )

    # that is an assumption, not sure if always true
    path = "/Applications/{}.app".format(appname)

    if not __salt__["file.find"](path):
        raise CommandExecutionError(
            "Could not find '{}.app' in /Applications".format(appname)
        )

    __salt__["log.info"]("Sending {} to trash.".format(path))
    trash(path)
    return True


def upgrade(name, user=None):
    """
    Upgrade whether an app.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.upgrade Telegram
        salt '*' mas.upgrade "747648890"

    name
        The name or ID of the app to upgrade. Passing
        a name will look up the ID of the most relevant search result.
        If you want to be precise, pass the numeric ID as a string.
        This avoids implicit casting issues.

    user
        The username to upgrade the app for. Defaults to salt user.

    """

    e = _which(user)

    # if not _is_id(name) and not (name := _get_local_id(name)):
    if not _is_id(name):
        name = _get_local_id(name)
        if not name:
            raise CommandExecutionError(
                "Could not find installation of '{}'.".format(name)
            )

    __salt__["log.info"]("mas is upgrading {}".format(name))

    return not __salt__["cmd.retcode"]("{} upgrade '{}'".format(e, name), runas=user)


def _get_current_version(name, user=None):
    appid = _get_local_id(name, user)
    installed = _list_installed(user, versions=True)
    return installed.get(appid)


def _get_latest_version(name, user=None):
    e = _which(user)
    appid = _get_local_id(name, user)
    out = __salt__["cmd.run_stdout"]("{} info '{}'".format(e, appid))
    header = out.splitlines()[0]
    step1 = header.rsplit("[", 1)[0].strip()
    return re.findall(r"[0-9\.]+$", step1)[0]


def _list_installed(user=None, versions=False):
    e = _which(user)
    ls = _parse_list(
        __salt__["cmd.run_stdout"]("{} list".format(e), raise_err=True, runas=user)
    )
    __salt__["log.info"]("mas list of installed apps: {}".format(ls))
    if versions:
        return {x[0]: x[2] for x in ls}
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
    ls = __salt__["cmd.run_stdout"](
        "{} search '{}'".format(e, name), raise_err=True, runas=user
    )
    try:
        res = _parse_list(ls)[0][0]
        __salt__["log.info"]("mas found id of app '{}': {}".format(name, res))
        return res
    except IndexError:
        return False


def _get_local_id(name, user=None):
    if _is_id(name):
        return str(name)
    for i, appname in _list_installed(user).items():
        if appname == name:
            __salt__["log.info"](
                "mas found id of installed app '{}': {}".format(name, i)
            )
            return i
    return False


def _get_local_name(appid, user=None):
    if not _is_id(appid):
        return appid
    for i, appname in _list_installed(user).items():
        if i == str(appid):
            __salt__["log.info"](
                "mas found name of installed app '{}': {}".format(appid, appname)
            )
            return appname
    return False


def _parse_list(ls):
    parsed = []
    if "No installed apps found" in ls:
        return []
    for x in ls.splitlines():
        x0, r = x.split(None, 1)
        r, x2 = r.rsplit(None, 1)
        x1 = r.strip()
        parsed.append((x0, x1, x2[1:-1]))
    return parsed
