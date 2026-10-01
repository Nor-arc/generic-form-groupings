"""Test fieldgroupsexamplemodel forms."""

from django.test import TestCase

from field_groups import forms


class FieldGroupsExampleModelTest(TestCase):
    """Test FieldGroupsExampleModel forms."""

    def test_specifying_all_fields_success(self):
        form = forms.FieldGroupsExampleModelForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.FieldGroupsExampleModelForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_fieldgroupsexamplemodel_is_required(self):
        form = forms.FieldGroupsExampleModelForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
