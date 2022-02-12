{%- from 'tool-mas/map.jinja' import mas -%}

include:
  - .package

{%- for user in mas.users | selectattr('mas.apps', 'defined') %}
  {%- for app in user.mas.apps %}
Mac App Store app '{{ app }}' is installed for user '{{ user.name }}':
  mas.installed:
    - name: '{{ app }}'
    - user: {{ user.name }}
    - require:
      - mas is installed
  {%- endfor %}
{%- endfor %}
