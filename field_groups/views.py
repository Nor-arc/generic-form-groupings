"""Views for field_groups."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.apps.ui import ObjectDetailContent, ObjectFieldsPanel, ObjectsTablePanel, SectionChoices
from nautobot.core.templatetags import helpers

from field_groups import filters, forms, models, tables
from field_groups.api import serializers


class FieldGroupsExampleModelUIViewSet(NautobotUIViewSet):
    """ViewSet for FieldGroupsExampleModel views."""

    bulk_update_form_class = forms.FieldGroupsExampleModelBulkEditForm
    filterset_class = filters.FieldGroupsExampleModelFilterSet
    filterset_form_class = forms.FieldGroupsExampleModelFilterForm
    form_class = forms.FieldGroupsExampleModelForm
    lookup_field = "pk"
    queryset = models.FieldGroupsExampleModel.objects.all()
    serializer_class = serializers.FieldGroupsExampleModelSerializer
    table_class = tables.FieldGroupsExampleModelTable

    # Here is an example of using the UI  Component Framework for the detail view.
    # More information can be found in the Nautobot documentation:
    # https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/
    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                # Alternatively, you can specify a list of field names:
                # fields=[
                #     "name",
                #     "description",
                # ],
                # Some fields may require additional configuration, we can use value_transforms
                # value_transforms={
                #     "name": [helpers.bettertitle]
                # },
            ),
            # If there is a ForeignKey or M2M with this model we can use ObjectsTablePanel
            # to display them in a table format.
            # ObjectsTablePanel(
                # weight=200,
                # section=SectionChoices.RIGHT_HALF,
                # table_class=tables.FieldGroupsExampleModelTable,
                # You will want to filter the table using the related_name
                # filter="fieldgroupsexamplemodels",
            # ),
        ],
    )
