"""Test FieldGroupsExampleModel."""

from nautobot.apps.testing import ModelTestCases

from field_groups import models
from field_groups.tests import fixtures


class TestFieldGroupsExampleModel(ModelTestCases.BaseModelTestCase):
    """Test FieldGroupsExampleModel."""

    model = models.FieldGroupsExampleModel

    @classmethod
    def setUpTestData(cls):
        """Create test data for FieldGroupsExampleModel Model."""
        super().setUpTestData()
        # Create 3 objects for the model test cases.
        fixtures.create_fieldgroupsexamplemodel()

    def test_create_fieldgroupsexamplemodel_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        fieldgroupsexamplemodel = models.FieldGroupsExampleModel.objects.create(name="Development")
        self.assertEqual(fieldgroupsexamplemodel.name, "Development")
        self.assertEqual(fieldgroupsexamplemodel.description, "")
        self.assertEqual(str(fieldgroupsexamplemodel), "Development")

    def test_create_fieldgroupsexamplemodel_all_fields_success(self):
        """Create FieldGroupsExampleModel with all fields."""
        fieldgroupsexamplemodel = models.FieldGroupsExampleModel.objects.create(name="Development", description="Development Test")
        self.assertEqual(fieldgroupsexamplemodel.name, "Development")
        self.assertEqual(fieldgroupsexamplemodel.description, "Development Test")
