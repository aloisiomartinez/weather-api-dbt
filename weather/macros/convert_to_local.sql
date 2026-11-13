{% macro convert_to_local(ts_col, offset_col) %}
 ({{ ts_col}} + make_interval(secs => {{ offset_col}}::integer))
 {% endmacro %}