"""Unit tests for views."""

from nautobot.apps.testing import ViewTestCases

from field_groups import models
from field_groups.tests import fixtures


class FieldGroupsExampleModelViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the FieldGroupsExampleModel views."""

    model = models.FieldGroupsExampleModel
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "description": "Initial model",
    }

    update_data = {
        "name": "Test 2",
        "description": "Updated model",
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_fieldgroupsexamplemodel()
