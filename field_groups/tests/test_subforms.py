"""Tests for `field_groups.subforms`: one declaration per kind, read by the model and the form alike."""

from django import forms
from django.test import SimpleTestCase

from field_groups.subforms import OptionsSubform
from field_groups.widgets import api_select_attrs


class VehicleOptionsForm(OptionsSubform):
    """A throwaway registry: what each kind of vehicle needs to know about itself."""

    selector = "kind"


class EngineOptionsMixin(forms.Form):
    """Shared by every motorised kind."""

    fuel = forms.ChoiceField(choices=[("petrol", "Petrol"), ("electric", "Electric")], initial="petrol")
    battery_kwh = forms.IntegerField(required=False, initial=0)

    field_conditions = {"battery_kwh": {"fuel": ("electric",)}}


class CarOptionsForm(EngineOptionsMixin, VehicleOptionsForm):
    """Cars have doors."""

    selected_by = ("car", "van")
    field_order = ["doors", "fuel", "battery_kwh"]

    doors = forms.IntegerField(initial=4)


class MotorbikeOptionsForm(EngineOptionsMixin, VehicleOptionsForm):
    """Motorbikes have an engine but no doors."""

    selected_by = ("motorbike",)


class BicycleOptionsForm(VehicleOptionsForm):
    """Bicycles have gears, and the form wants to know how many even though the model does not insist."""

    selected_by = ("bicycle",)
    ui_required = ("gears",)

    gears = forms.IntegerField(required=False)


class OptionsSubformTest(SimpleTestCase):
    """The registry, defaults and cleaning of one subform."""

    def test_a_subform_is_registered_for_each_value_it_declares(self):
        self.assertIs(VehicleOptionsForm.form_for("car"), CarOptionsForm)
        self.assertIs(VehicleOptionsForm.form_for("van"), CarOptionsForm)
        self.assertIs(VehicleOptionsForm.form_for("bicycle"), BicycleOptionsForm)
        self.assertIsNone(VehicleOptionsForm.form_for("skateboard"))

    def test_a_subclass_that_only_inherits_selected_by_does_not_replace_its_parent(self):
        class TweakedCarOptionsForm(CarOptionsForm):  # pylint: disable=unused-variable
            """Declares no values of its own."""

        self.assertIs(VehicleOptionsForm.form_for("car"), CarOptionsForm)

    def test_each_selector_has_its_own_registry(self):
        class OtherOptionsForm(OptionsSubform):
            selector = "other"

        class OnlyOtherOptionsForm(OtherOptionsForm):  # pylint: disable=unused-variable
            selected_by = ("x",)

        self.assertEqual(set(OtherOptionsForm.all_forms()), {"x"})
        self.assertNotIn("x", VehicleOptionsForm.all_forms())

    def test_missing_options_take_their_defaults(self):
        form = CarOptionsForm({"doors": 2})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.options, {"doors": 2, "fuel": "petrol", "battery_kwh": 0})

    def test_options_another_kind_reads_are_dropped(self):
        form = BicycleOptionsForm({"gears": 21, "doors": 4, "fuel": "electric"})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.options, {"gears": 21})

    def test_a_required_option_is_still_required(self):
        self.assertIn("doors", CarOptionsForm({"doors": ""}).errors)
        self.assertTrue(BicycleOptionsForm({"gears": ""}).is_valid())


class OptionsSubformFieldsTest(SimpleTestCase):
    """What the object's form takes from the subforms."""

    def test_all_fields_are_copied_once_each_in_render_order(self):
        fields = VehicleOptionsForm.all_fields()

        self.assertEqual(tuple(fields), ("doors", "fuel", "battery_kwh", "gears"))
        self.assertEqual(VehicleOptionsForm.field_names(), tuple(fields))
        self.assertIsNot(fields["doors"], CarOptionsForm.base_fields["doors"])  # pylint: disable=no-member
        self.assertEqual(fields["doors"].initial, 4)

    def test_each_field_shows_for_the_kinds_that_read_it(self):
        groups = {group.name: group for group in VehicleOptionsForm.field_groups()}

        self.assertEqual(tuple(groups), VehicleOptionsForm.field_names())
        self.assertEqual(set(groups["doors"].when["kind"]), {"car", "van"})
        self.assertEqual(set(groups["fuel"].when["kind"]), {"car", "van", "motorbike"})
        self.assertEqual(set(groups["gears"].when["kind"]), {"bicycle"})

    def test_a_conditional_field_also_waits_on_its_condition_and_is_required_when_shown(self):
        group = {group.name: group for group in VehicleOptionsForm.field_groups()}["battery_kwh"]

        self.assertEqual(group.when, {"kind": ("car", "van", "motorbike"), "fuel": ("electric",)})
        self.assertEqual(group.required, ("battery_kwh",))

    def test_ui_required_is_required_in_the_form_but_not_by_the_subform(self):
        group = {group.name: group for group in VehicleOptionsForm.field_groups()}["gears"]

        self.assertEqual(group.required, ("gears",))
        self.assertFalse(BicycleOptionsForm.base_fields["gears"].required)  # pylint: disable=no-member


class ApiSelectAttrsTest(SimpleTestCase):
    """`api_select_attrs` writes core's query-param attributes, including `$field` references."""

    def test_params_are_json_lists_as_core_writes_them(self):
        attrs = api_select_attrs("Choose...", content_type="$content_type", kind="aggregatable")

        self.assertEqual(
            attrs,
            {
                "display-field": "text",
                "data-placeholder": "Choose...",
                "data-query-param-content_type": '["$content_type"]',
                "data-query-param-kind": '["aggregatable"]',
            },
        )
