include:
  - package
{%- if mas.users | selectattr('mas.apps') %}
  - .apps
{%- endif %}
