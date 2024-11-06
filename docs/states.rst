Available states
----------------

The following states are found in this formula:

.. contents::
   :local:


``tool_mas``
~~~~~~~~~~~~
*Meta-state*.

Performs all operations described in this formula according to the specified configuration.


``tool_mas.package``
~~~~~~~~~~~~~~~~~~~~
Installs the mas package only.


``tool_mas.apps``
~~~~~~~~~~~~~~~~~



``tool_mas.clean``
~~~~~~~~~~~~~~~~~~
*Meta-state*.

Undoes everything performed in the ``tool_mas`` meta-state
in reverse order.


``tool_mas.package.clean``
~~~~~~~~~~~~~~~~~~~~~~~~~~
Removes the mas package.


``tool_mas.apps.clean``
~~~~~~~~~~~~~~~~~~~~~~~



