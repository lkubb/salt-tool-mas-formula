# vim: ft=sls

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_package_install = tplroot ~ ".package.install" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mas with context %}

include:
  - {{ sls_package_install }}


{%- for user in mas.users | selectattr("mas.apps", "defined") | selectattr("mas.apps") %}
{%-   for app in user.mas.apps.get("absent", []) %}

Mac App Store app '{{ app }}' is absent for user '{{ user.name }}':
  mas.absent:
    - name: '{{ app }}'
    - user: {{ user.name }}
    - require:
      - mas is installed
{%-   endfor %}

{%-   for app in user.mas.apps.get("wanted", []) %}

Mac App Store app '{{ app }}' is installed for user '{{ user.name }}':
  mas.installed:
    - name: '{{ app }}'
    - user: {{ user.name }}
    - require:
      - mas is installed
{%-   endfor %}
{%- endfor %}
