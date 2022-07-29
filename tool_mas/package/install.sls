# -*- coding: utf-8 -*-
# vim: ft=sls

{%- set tplroot = tpldir.split('/')[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as mas with context %}


mas is installed:
  pkg.installed:
    - name: {{ mas.lookup.pkg.name }}

mas setup is completed:
  test.nop:
    - name: Hooray, mas setup has finished.
    - require:
      - pkg: {{ mas.lookup.pkg.name }}
