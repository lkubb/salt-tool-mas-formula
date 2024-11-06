# vim: ft=sls

{#-
    *Meta-state*.

    Undoes everything performed in the ``tool_mas`` meta-state
    in reverse order.
#}

include:
  - .apps.clean
  - .package.clean
