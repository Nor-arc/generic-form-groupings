"""Models for Field Groups."""

from django.core.exceptions import ValidationError
from django.db import models
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.models import PrimaryModel, extras_features

from field_groups.choices import FuelChoices, VehicleKindChoices


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class FieldGroupsExampleModel(PrimaryModel):  # pylint: disable=too-many-ancestors
    """A vehicle: its `kind` decides which of the columns below it reads.

    `example_options.py` says which; `clean()` validates those and `save()` resets the rest, so the
    UI, REST API and bulk edit agree on what a record may hold.
    """

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True)
    kind = models.CharField(max_length=CHARFIELD_MAX_LENGTH, choices=VehicleKindChoices, default=VehicleKindChoices.CAR)
    # Read by some kinds only.
    doors = models.PositiveSmallIntegerField(default=0)
    fuel = models.CharField(max_length=CHARFIELD_MAX_LENGTH, choices=FuelChoices, blank=True, default="")
    battery_kwh = models.PositiveIntegerField(default=0)
    gears = models.PositiveSmallIntegerField(default=0)

    class Meta:
        """Meta class."""

        ordering = ["name"]

    def __str__(self):
        """Stringify instance."""
        return self.name

    def _normalize_options(self):
        """Clean the columns this kind reads, and reset the rest to their defaults.

        Run by both `clean()` and `save()`, so a record saved without validation (a REST bulk write)
        still drops what its kind does not read. Columns that do not validate are left as they are
        for `clean()` to report.

        Returns:
            (dict): The validation errors, keyed by field name; empty when the columns are valid.
        """
        # Imported here: the subforms carry core's form widgets, which cannot load until the app
        # registry is ready, and this module is imported while it is being populated.
        from field_groups.example_options import VehicleOptionsForm  # pylint: disable=import-outside-toplevel

        form_class = VehicleOptionsForm.form_for(self.kind)
        read = set(form_class.base_fields) if form_class else set()
        for name in VehicleOptionsForm.field_names():
            if name not in read:
                setattr(self, name, self._meta.get_field(name).get_default())
        if form_class is None:
            return {}
        form = form_class({name: getattr(self, name) for name in read})
        if not form.is_valid():
            return form.errors
        for name, value in form.options.items():
            setattr(self, name, value)
        return {}

    def clean(self):
        """Refuse columns the kind reads but cannot accept."""
        super().clean()
        errors = self._normalize_options()
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Reset the columns this kind does not read before saving."""
        self._normalize_options()
        super().save(*args, **kwargs)
