"""Tests for the declarative field groups in `field_groups.groups`."""

import json

from django import forms
from django.test import SimpleTestCase

from field_groups.groups import FieldGroup, FieldGroupsMixin


class ShippingForm(FieldGroupsMixin, forms.Form):
    """A throwaway form: courier details only for couriers, a tracking number only once dispatched."""

    method = forms.ChoiceField(choices=[("post", "Post"), ("courier", "Courier")])
    courier = forms.CharField(required=False)
    speed = forms.ChoiceField(choices=[("standard", "Standard"), ("express", "Express")], initial="standard")
    status = forms.ChoiceField(choices=[("new", "New"), ("dispatched", "Dispatched")], required=False)
    tracking = forms.CharField(required=False)

    field_groups = (
        FieldGroup("courier", fields=("courier", "speed"), when={"method": ("courier",)}, required=("courier",)),
        FieldGroup(
            "tracking",
            fields=("tracking",),
            when={"status": ("dispatched",)},
            unless={"speed": ("standard",)},
            required=("tracking",),
        ),
    )

    def __init__(self, *args, **kwargs):
        """Apply the groups last, as a real form does."""
        super().__init__(*args, **kwargs)
        self.apply_field_groups()


class FieldGroupTest(SimpleTestCase):
    """`FieldGroup.is_active` reads the values it is handed."""

    def test_when_requires_every_listed_value(self):
        group = FieldGroup("g", fields=("x",), when={"a": ("1",), "b": ("2",)})

        self.assertTrue(group.is_active({"a": "1", "b": "2"}.get))
        self.assertFalse(group.is_active({"a": "1", "b": "3"}.get))

    def test_unless_excludes_any_listed_value(self):
        group = FieldGroup("g", fields=("x",), unless={"a": ("1",)})

        self.assertFalse(group.is_active({"a": "1"}.get))
        self.assertTrue(group.is_active({"a": "2"}.get))

    def test_a_multi_value_field_matches_on_any_of_its_values(self):
        group = FieldGroup("g", fields=("x",), when={"a": ("2",)})

        self.assertTrue(group.is_active({"a": ["1", "2"]}.get))
        self.assertFalse(group.is_active({"a": []}.get))

    def test_values_compare_as_text(self):
        group = FieldGroup("g", fields=("x",), when={"a": (10,)})

        self.assertTrue(group.is_active({"a": "10"}.get))

    def test_a_group_without_conditions_is_always_active(self):
        self.assertTrue(FieldGroup("g", fields=("x",)).is_active({}.get))


class FieldGroupsMixinTest(SimpleTestCase):
    """`FieldGroupsMixin.apply_field_groups` on a bound and an unbound form."""

    def test_an_inactive_group_is_disabled_and_not_required(self):
        form = ShippingForm(data={"method": "post"})

        self.assertTrue(form.fields["courier"].disabled)
        self.assertFalse(form.fields["courier"].required)

    def test_an_active_group_requires_its_required_members(self):
        form = ShippingForm(data={"method": "courier"})

        self.assertFalse(form.fields["courier"].disabled)
        self.assertTrue(form.fields["courier"].required)
        self.assertFalse(form.is_valid())
        self.assertIn("courier", form.errors)

    def test_the_groups_read_initial_on_an_unbound_form(self):
        self.assertFalse(ShippingForm(initial={"method": "courier"}).fields["courier"].disabled)
        self.assertTrue(ShippingForm().fields["courier"].disabled)

    def test_a_stale_posted_value_for_an_inactive_field_is_ignored(self):
        form = ShippingForm(data={"method": "post", "courier": "Left over", "speed": "express"})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["courier"], "")
        self.assertEqual(form.cleaned_data["speed"], "standard")

    def test_a_field_an_inactive_group_disabled_holds_no_value_for_later_groups(self):
        """`speed` is only read while the courier group applies; otherwise `unless` cannot match it."""
        form = ShippingForm(data={"method": "post", "status": "dispatched", "speed": "standard"})

        self.assertFalse(form.fields["tracking"].disabled)

    def test_a_later_group_reads_an_earlier_active_group_s_value(self):
        form = ShippingForm(data={"method": "courier", "courier": "Acme", "status": "dispatched", "speed": "standard"})

        self.assertTrue(form.fields["tracking"].disabled)

    def test_the_markup_carries_the_conditions(self):
        form = ShippingForm()

        attrs = str(form["tracking"])

        self.assertIn('data-field-group="tracking"', attrs)
        self.assertIn('data-field-group-index="1"', attrs)
        when = json.dumps({"status": ["dispatched"]}).replace('"', "&quot;")
        self.assertIn(f'data-field-group-when="{when}"', attrs)
        self.assertEqual(form.fields["courier"].widget.attrs.get("data-required-when-active"), "")
        self.assertNotIn("data-required-when-active", form.fields["speed"].widget.attrs)

    def test_an_inactive_field_renders_disabled_and_marked_for_the_stylesheet(self):
        self.assertIn("disabled", str(ShippingForm()["courier"]))
        self.assertIn("data-field-group-inactive", str(ShippingForm()["courier"]))
        self.assertNotIn("data-field-group-inactive", str(ShippingForm(initial={"method": "courier"})["courier"]))

    def test_has_missing_required_follows_the_active_groups(self):
        self.assertTrue(ShippingForm(data={"method": "courier"}).has_missing_required)
        self.assertFalse(ShippingForm(data={"method": "post"}).has_missing_required)
        self.assertTrue(ShippingForm(data={}).has_missing_required)
