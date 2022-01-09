# `mas` Formula
Makes sure `mas` and specified Mac App Store apps are installed and provides a custom execution module/state to manage mas inside salt.

## Usage
Applying `tool-mas` will make sure `mas` is configured as specified and requested apps are installed.

### Execution module and state
This formula provides a custom execution module and state to manage apps installed with mas. The `name` parameter can either be a name (which will result in a lucky style installation by installing the most relevant search result) or an ID (recommended to make sure the correct app is installed). The functions are self-explanatory, please see the source code for comments. Currently, the following states are supported:
* `mas.installed(name, user)`
* `mas.absent(name, user)`
* `mas.latest(name, user)`

## Configuration
### Pillar
#### General `tool` architecture
Since installing user environments is not the primary use case for saltstack, the architecture is currently a bit awkward. All `tool` formulas assume running as root. There are three scopes of configuration:
1. per-user `tool`-specific
  > e.g. generally force usage of XDG dirs in `tool` formulas for this user
2. per-user formula-specific
  > e.g. setup this tool with the following configuration values for this user
3. global formula-specific (All formulas will accept `defaults` for `users:username:formula` default values in this scope as well.)
  > e.g. setup system-wide configuration files like this

**3** goes into `tool:formula` (e.g. `tool:git`). Both user scopes (**1**+**2**) are mixed per user in `users`. `users` can be defined in `tool:users` and/or `tool:formula:users`, the latter taking precedence. (**1**) is namespaced directly under `username`, (**2**) is namespaced under `username: {formula: {}}`.

```yaml
tool:
######### user-scope 1+2 #########
  users:                         #
    username:                    #
      xdg: true                  #
      dotconfig: true            #
      formula:                   #
        config: value            #
####### user-scope 1+2 end #######
  formula:
    formulaspecificstuff:
      conf: val
    defaults:
      yetanotherconfig: somevalue
######### user-scope 1+2 #########
    users:                       #
      username:                  #
        xdg: false               #
        formula:                 #
          otherconfig: otherval  #
####### user-scope 1+2 end #######
```

#### User-specific
The following shows an example of `tool-mas` pillar configuration. Namespace it to `tool:users` and/or `tool:mas:users`.
```yaml
user:
  apps:
    - Telegram    # specifying by name will install lucky-style (most relevant search result)
    - 747648890   # specifying by id will make sure the correct app is installed
```

#### Formula-specific
```yaml
tool:
  mas:
    defaults:           # default apps for all users
      apps:
        - 747648890
```

## Todo
- fix mas.remove error. this might work with doing the [work in python directly](https://github.com/arsenetar/send2trash) (mas just moves to trash)
```python
# Copyright 2017 Virgil Dupras

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

# I modified it to be completely standalone

from __future__ import unicode_literals

from ctypes import cdll, byref, Structure, c_char, c_char_p
from ctypes.util import find_library

Foundation = cdll.LoadLibrary(find_library("Foundation"))
CoreServices = cdll.LoadLibrary(find_library("CoreServices"))

GetMacOSStatusCommentString = Foundation.GetMacOSStatusCommentString
GetMacOSStatusCommentString.restype = c_char_p
FSPathMakeRefWithOptions = CoreServices.FSPathMakeRefWithOptions
FSMoveObjectToTrashSync = CoreServices.FSMoveObjectToTrashSync

kFSPathMakeRefDefaultOptions = 0
kFSPathMakeRefDoNotFollowLeafSymlink = 0x01

kFSFileOperationDefaultOptions = 0
kFSFileOperationOverwrite = 0x01
kFSFileOperationSkipSourcePermissionErrors = 0x02
kFSFileOperationDoNotMoveAcrossVolumes = 0x04
kFSFileOperationSkipPreflight = 0x08


class FSRef(Structure):
    _fields_ = [("hidden", c_char * 80)]


def check_op_result(op_result):
    if op_result:
        msg = GetMacOSStatusCommentString(op_result).decode("utf-8")
        raise OSError(msg)


def send2trash(path):
    path = path.encode("utf-8") if not isinstance(path, bytes) else path
    fp = FSRef()
    opts = kFSPathMakeRefDoNotFollowLeafSymlink
    op_result = FSPathMakeRefWithOptions(path, opts, byref(fp), None)
    check_op_result(op_result)
    opts = kFSFileOperationDefaultOptions
    op_result = FSMoveObjectToTrashSync(byref(fp), None, opts)
    check_op_result(op_result)
```
