"""Filtering for field_groups."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from field_groups import models


class FieldGroupsExampleModelFilterSet(NameSearchFilterSet, NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for FieldGroupsExampleModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.FieldGroupsExampleModel

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"
