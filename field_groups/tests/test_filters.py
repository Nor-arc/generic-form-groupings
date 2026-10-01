"""Test FieldGroupsExampleModel Filter."""

from nautobot.apps.testing import FilterTestCases

from field_groups import filters, models
from field_groups.tests import fixtures


class FieldGroupsExampleModelFilterTestCase(FilterTestCases.FilterTestCase):  # pylint: disable=too-many-ancestors
    """FieldGroupsExampleModel Filter Test Case."""

    queryset = models.FieldGroupsExampleModel.objects.all()
    filterset = filters.FieldGroupsExampleModelFilterSet
    generic_filter_tests = (
        ("id",),
        ("created",),
        ("last_updated",),
        ("name",),
    )

    @classmethod
    def setUpTestData(cls):
        """Setup test data for FieldGroupsExampleModel Model."""
        fixtures.create_fieldgroupsexamplemodel()

    def test_q_search_name(self):
        """Test using Q search with name of FieldGroupsExampleModel."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for FieldGroupsExampleModel."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
