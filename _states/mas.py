"""
Manage Mac App Store apps with mas
======================================================

"""

# import logging
import salt.exceptions

# import salt.utils.platform

# log = logging.getLogger(__name__)

__virtualname__ = "mas"


def __virtual__():
    """
    Only work on Mac OS
    """
    if salt.utils.platform.is_darwin():
        return __virtualname__
    return False


def installed(name, user=None):
    """
    Make sure App Store app is installed.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.installed telegram

    name
        The name or ID of the app to install, if not installed already. Passing
        a name will install the first hit when searching for the term. If you
        want to be precise, pass the numeric ID.

    user
        The username to install the app for. Defaults to salt user.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    try:
        if __salt__["mas.is_installed"](name, user):
            ret["comment"] = "App is already installed."
        elif __opts__['test']:
            ret['result'] = None
            ret['comment'] = "App '{}' would have been installed for user '{}'.".format(name, user)
            ret["changes"] = {'installed': name}
        elif __salt__["mas.install"](name, user):
            ret["comment"] = "App '{}' was installed for user '{}'.".format(name, user)
            ret["changes"] = {'installed': name}
        else:
            ret["result"] = False
            ret["comment"] = "Something went wrong while calling mas."
    except salt.exceptions.CommandExecutionError as e:
        ret["result"] = False
        ret["comment"] = str(e)

    return ret


def latest(name, user=None):
    """
    Make sure app is installed and up to date.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.latest telegram

    name
        The name or ID of the app to upgrade or install, if not installed already.
        Passing a name will install the first hit when searching for the term.
        If you want to be precise, pass the numeric ID.

    user
        The username to install the app for. Defaults to salt user.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    try:
        if __salt__["mas.is_installed"](name, user):
            if __opts__['test']:
                ret['result'] = None
                ret['comment'] = "App '{}' would have been upgraded for user '{}'.".format(name, user)
                ret["changes"] = {'installed': name}
            elif __salt__["mas.upgrade"](name, user):
                ret["comment"] = "App '{}' was upgraded for user '{}'.".format(name, user)
                ret["changes"] = {'upgraded': name}
            else:
                ret["result"] = False
                ret["comment"] = "Something went wrong while calling mas."
        elif __opts__['test']:
            ret['result'] = None
            ret['comment'] = "App '{}' would have been installed for user '{}'.".format(name, user)
            ret["changes"] = {'installed': name}
        elif __salt__["mas.install"](name, user):
            ret["comment"] = "App '{}' was installed for user '{}'.".format(name, user)
            ret["changes"] = {'installed': name}
        else:
            ret["result"] = False
            ret["comment"] = "Something went wrong while calling mas."
        return ret

    except salt.exceptions.CommandExecutionError as e:
        ret["result"] = False
        ret["comment"] = str(e)

    return ret


def absent(name, user=None):
    """
    Make sure App Store app is removed.

    CLI Example:

    .. code-block:: bash

        salt '*' mas.absent telegram

    name
        The name or ID of the app to remove, if installed.
        Passing a name will install the first hit when searching for the term.
        If you want to be precise, pass the numeric ID.

    user
        The username to remove the app for. Defaults to salt user.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    try:
        if not __salt__["mas.is_installed"](name, user):
            ret["comment"] = "App is already absent."
            return ret
        elif __opts__['test']:
            ret['result'] = None
            ret['comment'] = "App '{}' would have been removed for user '{}'.".format(name, user)
            ret["changes"] = {'installed': name}
        elif __salt__["mas.remove"](name, user):
            ret["comment"] = "App '{}' was removed for user '{}'.".format(name, user)
            ret["changes"] = {'installed': name}
        else:
            ret["result"] = False
            ret["comment"] = "Something went wrong while calling mas."
    except salt.exceptions.CommandExecutionError as e:
        ret["result"] = False
        ret["comment"] = str(e)

    return ret
