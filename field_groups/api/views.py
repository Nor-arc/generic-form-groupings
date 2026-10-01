"""API views for field_groups."""

from nautobot.apps.api import NautobotModelViewSet

from field_groups import filters, models
from field_groups.api import serializers


class FieldGroupsExampleModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """FieldGroupsExampleModel viewset."""

    queryset = models.FieldGroupsExampleModel.objects.all()
    serializer_class = serializers.FieldGroupsExampleModelSerializer
    filterset_class = filters.FieldGroupsExampleModelFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
