"""Which of `FieldGroupsExampleModel`'s columns each kind of vehicle reads, declared once as subforms.

`FieldGroupsExampleModel.clean()` and `save()` validate and reset the columns through these, and
`FieldGroupsExampleModelForm` takes its fields and `FieldGroup`s from them. Adding a column is a
model field and one form field here; adding a kind is a choice and one subform here.
"""

from django import forms
from nautobot.apps.forms import StaticSelect2

from field_groups.choices import FuelChoices
from field_groups.subforms import OptionsSubform


class VehicleOptionsForm(OptionsSubform):
    """The registry: a vehicle's `kind` picks which subform describes it."""

    selector = "kind"


class EngineOptionsMixin(forms.Form):
    """Shared by every motorised kind: the fuel, and a battery size when it is electric."""

    fuel = forms.ChoiceField(choices=FuelChoices, initial=FuelChoices.PETROL, widget=StaticSelect2)
    battery_kwh = forms.IntegerField(required=False, initial=0, label="Battery capacity (kWh)")

    field_conditions = {"battery_kwh": {"fuel": (FuelChoices.ELECTRIC,)}}

    def clean(self):
        """An electric vehicle must say how big its battery is; any other drops a stray size."""
        cleaned_data = super().clean()
        if cleaned_data.get("fuel") == FuelChoices.ELECTRIC:
            if not cleaned_data.get("battery_kwh"):
                self.add_error("battery_kwh", "Battery capacity is required for an electric vehicle.")
        else:
            cleaned_data["battery_kwh"] = 0
        return cleaned_data


class CarOptionsForm(EngineOptionsMixin, VehicleOptionsForm):
    """Cars and vans: an engine and a number of doors."""

    selected_by = ("car", "van")
    field_order = ["doors", "fuel", "battery_kwh"]

    doors = forms.IntegerField(min_value=1, initial=4)


class MotorbikeOptionsForm(EngineOptionsMixin, VehicleOptionsForm):
    """Motorbikes: an engine but no doors."""

    selected_by = ("motorbike",)


class BicycleOptionsForm(VehicleOptionsForm):
    """Bicycles: gears only. The form asks for them, though a record may be saved without."""

    selected_by = ("bicycle",)
    ui_required = ("gears",)

    gears = forms.IntegerField(required=False, min_value=1)
