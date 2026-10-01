"""Declarative field groups: fields a form shows, validates and saves only under given conditions.

A form lists its `FieldGroup`s once, and every layer reads that one declaration:

- The server (`FieldGroupsMixin.apply_field_groups()`) disables an inactive group's fields, so Django
  ignores whatever was posted for them and cleans them to their defaults, and marks an active
  group's `required` fields required.
- Each grouped field's widget carries the group's conditions as `data-field-group-*` attributes, so
  any template that renders the widget, core's `render_field` included, emits them.
- `static/field_groups/js/field_groups.js` re-evaluates the same conditions in the browser on every
  change, toggling visibility, `disabled` and `required` to match.

A form declares which fields depend on which values; nothing here knows what the fields are.
"""

import json
from dataclasses import dataclass, field

from django.core.exceptions import FieldDoesNotExist


def _as_values(value):
    """A field's value as a list of strings: none, one, or several (a multi-select). Blanks are no value."""
    items = value if isinstance(value, (list, tuple)) else [value]
    return [str(item) for item in items if item not in (None, "")]


@dataclass(frozen=True)
class FieldGroup:
    """Fields that only apply while other fields hold given values.

    Attributes:
        name (str): Identifies the group in the markup (`data-field-group`).
        fields (tuple): Names of the member fields.
        when (dict): Field name to allowed values; every listed field must hold one of its values.
        unless (dict): Field name to excluded values; no listed field may hold one of its values.
        required (tuple): Members that are required while the group is active.
    """

    name: str
    fields: tuple
    when: dict = field(default_factory=dict)
    unless: dict = field(default_factory=dict)
    required: tuple = ()

    def is_active(self, value_of):
        """Whether the group applies, given `value_of(name)`, which returns a field's current value."""

        def holds(name, allowed):
            return any(value in {str(item) for item in allowed} for value in _as_values(value_of(name)))

        return all(holds(name, allowed) for name, allowed in self.when.items()) and not any(
            holds(name, excluded) for name, excluded in self.unless.items()
        )


class FieldGroupsMixin:
    """Apply a form's `field_groups` to its fields. Mix in ahead of the form class.

    The form calls `apply_field_groups()` at the end of its own `__init__`, once `initial` is
    settled, because the conditions read each field's current value (`self[name].value()`: the
    posted data when bound, else `initial` or the instance), so create, a failed submit, edit and
    clone all resolve alike.
    """

    field_groups = ()

    def apply_field_groups(self):
        """Disable and reset inactive groups' fields; require active groups' `required` fields.

        Groups are evaluated in declaration order, and a field an earlier inactive group disabled
        counts as holding no value, just as the browser posts nothing for a disabled control.
        """
        self._inactive_group_fields = set()
        for index, group in enumerate(self.field_groups):
            active = group.is_active(lambda name: None if name in self._inactive_group_fields else self[name].value())
            attrs = {
                "data-field-group": group.name,
                "data-field-group-index": index,
                "data-field-group-when": json.dumps(group.when),
                "data-field-group-unless": json.dumps(group.unless),
            }
            for name in group.fields:
                form_field = self.fields[name]
                form_field.widget.attrs.update(attrs)  # escaped by Django when rendered
                form_field.required_when_active = name in group.required
                if form_field.required_when_active:
                    form_field.widget.attrs["data-required-when-active"] = ""
                if active:
                    if form_field.required_when_active:
                        form_field.required = True
                    continue
                # Django ignores posted data for a disabled field and cleans it to its initial value,
                # so a stale value never reaches the instance.
                form_field.required = False
                form_field.disabled = True
                # Lets `static/field_groups/css/field_groups.css` hide the row before any script runs.
                form_field.widget.attrs["data-field-group-inactive"] = ""
                self.initial[name] = self._field_group_default(name)
                self._inactive_group_fields.add(name)

    def _field_group_default(self, name):
        """What an inactive field saves: its form field's `initial`, else its model field's default."""
        if self.fields[name].initial is not None:
            return self.fields[name].initial
        model = getattr(getattr(self, "_meta", None), "model", None)
        try:
            return model._meta.get_field(name).get_default() if model is not None else None
        except FieldDoesNotExist:
            return None

    @property
    def has_missing_required(self):
        """Whether any required, enabled field has no value yet; readable before `is_valid()`."""
        return any(
            form_field.required and not form_field.disabled and not _as_values(self[name].value())
            for name, form_field in self.fields.items()
        )

    def _post_clean(self):
        """Put an inactive field's default on the instance before `construct_instance()` runs.

        `construct_instance()` skips a field that was left out of the POST and has an empty value
        and a model default, keeping whatever the instance held: an edited object would keep a value for a field its
        group no longer applies to. Setting it here first makes the default stick.
        """
        instance = getattr(self, "instance", None)  # a plain Form has none
        for name in getattr(self, "_inactive_group_fields", ()):
            if instance is not None and name in self.cleaned_data and hasattr(instance, name):
                setattr(instance, name, self.cleaned_data[name])
        super()._post_clean()
