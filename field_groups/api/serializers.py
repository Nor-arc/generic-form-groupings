"""API serializers for field_groups."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from field_groups import models


class FieldGroupsExampleModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """FieldGroupsExampleModel Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.FieldGroupsExampleModel
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []
