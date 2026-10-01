"""Options subforms: the fields one choice of a selector field reads, declared once and used everywhere.

A model may hold columns that only some of its kinds read: a bar chart groups and aggregates, a
gauge counts named values of one field, and the kind is a choice on one column (the selector). Each
kind declares the fields it reads as a small Django form, complete down to its widgets, and from
those declarations:

- a model's `clean()` validates the columns its kind reads (`OptionsSubform.form_for()`) and its
  `save()` resets the rest (`field_names()`), so the UI, REST API and bulk edit agree on what an
  object may hold;
- the object's form copies the fields (`all_fields()`) and shows each only for the choices that read
  it (`field_groups()`, as `FieldGroup`s for `FieldGroupsMixin`), so it needs no list of its own.

A base subclass names the selector and starts a registry; each subclass of it that declares
`selected_by` joins that registry for those choices:

    class ChartOptionsForm(OptionsSubform):
        selector = "chart_type"

    class GaugeOptionsForm(ChartOptionsForm):
        selected_by = ("gauge",)
        gauge_field = forms.CharField()
"""

from __future__ import annotations

import copy

from django import forms

from field_groups.groups import FieldGroup


class OptionsSubform(forms.Form):
    """Validate the settings one choice of the selector reads, filling in defaults for any left out.

    Attributes:
        selector (str): The field whose value picks the subform. Setting it starts a registry.
        selected_by (tuple): The selector values this subform describes. Setting it registers the
            subform for them in the nearest registry.
        ui_required (tuple): Fields the object's form requires although the object may be saved
            without them.
        field_conditions (dict): Field name to `{other field: values}` it additionally depends on
            in the object's form, beyond the selector.
        field_order (list): The order the object's form renders these fields in.
    """

    selector = None
    selected_by = ()
    ui_required = ()
    field_conditions = {}

    def __init_subclass__(cls, **kwargs):
        """Start a registry for a class that names a selector; register one that declares `selected_by` itself."""
        super().__init_subclass__(**kwargs)
        if "selector" in cls.__dict__:
            cls._registry = {}
        for value in cls.__dict__.get("selected_by", ()):
            cls._registry[value] = cls

    def __init__(self, options=None):
        """Bind `options`, with each field's `initial` standing in for a key that is missing.

        Args:
            options (dict): Setting name to value, as the object's columns hold them.
        """
        data = {
            name: field.initial() if callable(field.initial) else field.initial
            for name, field in self.base_fields.items()  # pylint: disable=no-member
            if field.initial is not None
        }
        data.update(options or {})
        super().__init__(data=data)

    @property
    def options(self):
        """The cleaned settings, keyed by field name. Call after `is_valid()`."""
        return {name: self.cleaned_data[name] for name in self.fields if name in self.cleaned_data}

    @classmethod
    def all_forms(cls) -> dict[str, type[OptionsSubform]]:
        """Selector value to the subform registered for it."""
        return dict(cls._registry)

    @classmethod
    def form_for(cls, value):
        """The subform for selector value `value`, or `None` for a choice that reads no options."""
        return cls._registry.get(value)

    @classmethod
    def _forms(cls):
        """Each subform once, in definition order, which is the order its fields render."""
        return list(dict.fromkeys(cls._registry.values()))

    @classmethod
    def all_fields(cls):
        """Every field, once each, copied from the subforms in render order.

        A field two subforms share through a common mixin is one field.

        Returns:
            (dict): Field name to a fresh copy of its field.
        """
        fields = {}
        for form_class in cls._forms():
            for name in form_class.field_order or list(form_class.base_fields):
                if name not in fields:
                    fields[name] = copy.deepcopy(form_class.base_fields[name])
        return fields

    @classmethod
    def field_names(cls):
        """Every field some choice reads, in render order."""
        return tuple(cls.all_fields())

    @classmethod
    def field_groups(cls):
        """One `FieldGroup` per field, shown for exactly the choices whose subform declares it.

        In `field_names()` order, which the groups rely on: a field whose conditions read another
        comes after it.

        Returns:
            (tuple): The groups.
        """
        groups = []
        for name in cls.field_names():
            form_classes = [form_class for form_class in cls._forms() if name in form_class.base_fields]
            values = tuple(value for form_class in form_classes for value in form_class.selected_by)
            conditions = {}
            for form_class in form_classes:
                conditions.update(form_class.field_conditions.get(name, {}))
            required = any(
                form_class.base_fields[name].required or name in form_class.ui_required for form_class in form_classes
            )
            # A field that waits on another field's value is required whenever it shows.
            required = required or bool(conditions)
            groups.append(
                FieldGroup(
                    name,
                    fields=(name,),
                    when={cls.selector: values, **conditions},
                    required=(name,) if required else (),
                )
            )
        return tuple(groups)
