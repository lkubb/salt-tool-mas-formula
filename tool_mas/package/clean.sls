# vim: ft=sls

{#-
    Removes the mas package.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_config_clean = tplroot ~ ".config.clean" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mas with context %}

include:
  - {{ sls_config_clean }}


mas is removed:
  pkg.removed:
    - name: {{ mas.lookup.pkg.name }}
    - require:
      - sls: {{ sls_config_clean }}
