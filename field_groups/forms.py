"""Forms for field_groups."""

from django import forms
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.forms import (
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    StaticSelect2,
    TagsBulkEditFormMixin,
    add_blank_choice,
)

from field_groups import models
from field_groups.choices import VehicleKindChoices
from field_groups.example_options import VehicleOptionsForm
from field_groups.groups import FieldGroupsMixin

# Every kind's option fields, as the subforms declare them, for the model form to inherit in place
# of the ones the ModelForm would generate from the columns.
VehicleOptionFields = type(
    "VehicleOptionFields",
    (forms.Form,),
    {"__module__": __name__, **VehicleOptionsForm.all_fields()},
)


class FieldGroupsExampleModelForm(FieldGroupsMixin, NautobotModelForm, VehicleOptionFields):  # pylint: disable=too-many-ancestors
    """FieldGroupsExampleModel creation/edit form: shows each option field for the kinds that read it."""

    field_groups = VehicleOptionsForm.field_groups()

    kind = forms.ChoiceField(choices=VehicleKindChoices, initial=VehicleKindChoices.CAR, widget=StaticSelect2)

    class Meta:
        """Meta attributes."""

        model = models.FieldGroupsExampleModel
        fields = ["name", "description", "kind", *VehicleOptionsForm.field_names()]

    def __init__(self, *args, **kwargs):
        """Apply the groups last, once `initial` is settled from the instance or the POST."""
        super().__init__(*args, **kwargs)
        self.apply_field_groups()


class FieldGroupsExampleModelBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """FieldGroupsExampleModel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.FieldGroupsExampleModel.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False, max_length=CHARFIELD_MAX_LENGTH)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class FieldGroupsExampleModelFilterForm(NautobotFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form to filter searches."""

    model = models.FieldGroupsExampleModel
    field_order = ["q", "name", "kind"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")
    kind = forms.ChoiceField(choices=add_blank_choice(VehicleKindChoices), required=False, widget=StaticSelect2)
