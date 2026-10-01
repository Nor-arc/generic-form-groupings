"""Create fixtures for tests."""

from field_groups.models import FieldGroupsExampleModel


def create_fieldgroupsexamplemodel():
    """Fixture to create necessary number of FieldGroupsExampleModel for tests."""
    FieldGroupsExampleModel.objects.create(name="Test One")
    FieldGroupsExampleModel.objects.create(name="Test Two")
    FieldGroupsExampleModel.objects.create(name="Test Three")
