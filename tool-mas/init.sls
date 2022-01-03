{%- from 'tool-mas/map.jinja' import mas -%}

include:
  - .package
{%- if mas.users | selectattr('mas.apps', 'defined') %}
  - .apps
{%- endif %}
