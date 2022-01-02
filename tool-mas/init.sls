include:
  - package
{%- if mas.users | selectattr('mas.apps', 'defined') %}
  - .apps
{%- endif %}
