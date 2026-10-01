"""Widget attributes for core's API selects that other fields' values feed."""

import json


def api_select_attrs(placeholder, **query_params):
    """Attributes for an API select: its placeholder, and query params as core's `add_query_param` writes them.

    A value of `"$name"` makes the select send field `name`'s value, and marks the select as depending
    on it (`static/field_groups/js/dependent_selects.js` empties it when `name` changes).

    Args:
        placeholder (str): Shown while nothing is chosen.
        **query_params: Query parameter name to its value, or `"$name"` to read field `name`.

    Returns:
        (dict): Widget attributes for `APISelect(attrs=...)`.
    """
    attrs = {"display-field": "text", "data-placeholder": placeholder}
    for name, value in query_params.items():
        attrs[f"data-query-param-{name}"] = json.dumps([str(value)], ensure_ascii=False)
    return attrs
