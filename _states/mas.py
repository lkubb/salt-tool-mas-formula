"""
Manage Mac App Store apps with mas
======================================================

"""

import salt.exceptions
import salt.utils.platform

__virtualname__ = "mas"


def __virtual__():
    """
    Only work on Mac OS
    """
    if salt.utils.platform.is_darwin():
        return __virtualname__
    return False


def installed(name):
    """
    Make sure App Store app is installed.

    name
        The name or ID of the app to install, if not installed already. Passing
        a name will install the first hit when searching for the term. If you
        want to be precise, pass the numeric ID.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    try:
        if __salt__["mas.is_installed"](name):
            ret["comment"] = "App is already installed."
        elif __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"App '{name}' would have been installed."
            ret["changes"] = {"installed": name}
        else:
            __salt__["mas.install"](name)
            ret["comment"] = f"App '{name}' was installed."
            ret["changes"] = {"installed": name}
    except salt.exceptions.CommandExecutionError as err:
        ret["result"] = False
        ret["comment"] = str(err)

    return ret


def latest(name):
    """
    Make sure an App Store app is installed and up to date.

    name
        The name or ID of the app to upgrade or install, if not installed already.
        Passing a name will install the first hit when searching for the term.
        If you want to be precise, pass the numeric ID.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    try:
        if __salt__["mas.is_installed"](name):
            if not __salt__["mas.is_outdated"](name):
                ret["comment"] = f"App '{name}' is already up to date."
            elif __opts__["test"]:
                ret["result"] = None
                ret["comment"] = f"App '{name}' would have been upgraded."
                ret["changes"] = {"upgraded": name}
            else:
                __salt__["mas.upgrade"](name)
                ret["comment"] = f"App '{name}' was upgraded."
                ret["changes"] = {"upgraded": name}
        else:
            return installed(name)

    except salt.exceptions.CommandExecutionError as err:
        ret["result"] = False
        ret["comment"] = str(err)

    return ret


def absent(name):
    """
    Make sure an App Store app is removed.

    name
        The name or ID of the app to remove, if installed.
        Passing a name will install the first hit when searching for the term.
        If you want to be precise, pass the numeric ID.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    try:
        if not __salt__["mas.is_installed"](name):
            ret["comment"] = "App is already absent."
            return ret
        elif __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"App '{name}' would have been removed."
            ret["changes"] = {"removed": name}
        else:
            __salt__["mas.remove"](name)
            ret["comment"] = f"App '{name}' was removed."
            ret["changes"] = {"removed": name}
    except salt.exceptions.CommandExecutionError as err:
        ret["result"] = False
        ret["comment"] = str(err)

    return ret
