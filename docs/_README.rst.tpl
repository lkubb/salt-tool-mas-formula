.. _readme:

mas Formula
===========

Manages mas in the user environment. Makes sure specified Mac App Store apps are installed and provides a custom execution module/state to manage mas inside salt.

.. contents:: **Table of Contents**
   :depth: 1

Usage
-----
Applying ``tool_mas`` will make sure ``mas`` is configured as specified.

Execution and state module
~~~~~~~~~~~~~~~~~~~~~~~~~~
This formula provides a custom execution module and state to manage packages installed with mas. The `name` parameter can either be a name (which will result in a lucky style installation by installing the most relevant search result) or an ID (recommended to make sure the correct app is installed). The functions are self-explanatory, please see the source code or the rendered docs at :ref:`em_mas` and :ref:`sm_mas`.

Configuration
-------------

This formula
~~~~~~~~~~~~
The general configuration structure is in line with all other formulae from the `tool` suite, for details see :ref:`toolsuite`. An example pillar is provided, see :ref:`pillar.example`. Note that you do not need to specify everything by pillar. Often, it's much easier and less resource-heavy to use the ``parameters/<grain>/<value>.yaml`` files for non-sensitive settings. The underlying logic is explained in :ref:`map.jinja`.

User-specific
^^^^^^^^^^^^^
The following shows an example of ``tool_mas`` per-user configuration. If provided by pillar, namespace it to ``tool_global:users`` and/or ``tool_mas:users``. For the ``parameters`` YAML file variant, it needs to be nested under a ``values`` parent key. The YAML files are expected to be found in

1. ``salt://tool_mas/parameters/<grain>/<value>.yaml`` or
2. ``salt://tool_global/parameters/<grain>/<value>.yaml``.

.. code-block:: yaml

  user:

      # Persist environment variables used by this formula for this
      # user to this file (will be appended to a file relative to $HOME)
    persistenv: '.config/zsh/zshenv'

      # Add runcom hooks specific to this formula to this file
      # for this user (will be appended to a file relative to $HOME)
    rchook: '.config/zsh/zshrc'

      # This user's configuration for this formula. Will be overridden by
      # user-specific configuration in `tool_mas:users`.
      # Set this to `false` to disable configuration for this user.
    mas:
          # make sure apps are installed/absent
        apps:
          absent:
            - '1147396723'
          wanted:
              # Specifying by ID will make sure the correct app is installed.
            - '747648890'
              # Specifying by name will install lucky-style
              # (most relevant search result).
            - Telegram

Formula-specific
^^^^^^^^^^^^^^^^

.. code-block:: yaml

  tool_mas:

      # Specify an explicit version (works on most Linux distributions) or
      # keep the packages updated to their latest version on subsequent runs
      # by leaving version empty or setting it to 'latest'
      # (again for Linux, brew does that anyways).
    version: latest

      # Default formula configuration for all users.
    defaults:
      apps: default value for all users

<INSERT_STATES>

Development
-----------

Contributing to this repo
~~~~~~~~~~~~~~~~~~~~~~~~~

Commit messages
^^^^^^^^^^^^^^^

Commit message formatting is significant.

Please see `How to contribute <https://github.com/saltstack-formulas/.github/blob/master/CONTRIBUTING.rst>`_ for more details.

pre-commit
^^^^^^^^^^

`pre-commit <https://pre-commit.com/>`_ is configured for this formula, which you may optionally use to ease the steps involved in submitting your changes.
First install  the ``pre-commit`` package manager using the appropriate `method <https://pre-commit.com/#installation>`_, then run ``bin/install-hooks`` and
now ``pre-commit`` will run automatically on each ``git commit``.

.. code-block:: console

  $ bin/install-hooks
  pre-commit installed at .git/hooks/pre-commit
  pre-commit installed at .git/hooks/commit-msg

State documentation
~~~~~~~~~~~~~~~~~~~
There is a script that semi-autodocuments available states: ``bin/slsdoc``.

If a ``.sls`` file begins with a Jinja comment, it will dump that into the docs. It can be configured differently depending on the formula. See the script source code for details currently.

This means if you feel a state should be documented, make sure to write a comment explaining it.

Todo
----
* fix ``mas.latest`` state (check if packages are up to date with `mas info` version vs `mas list` version) and don't run if not upgradeable (currently fails with ``something went wrong while calling mas``. also not sure if upgrading a single app is possible
