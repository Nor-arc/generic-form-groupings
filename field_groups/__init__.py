"""App declaration for field_groups."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class FieldGroupsConfig(NautobotAppConfig):
    """App configuration for the field_groups app."""

    name = "field_groups"
    verbose_name = "Field Groups"
    version = __version__
    author = "Network to Code, LLC"
    description = "Field Groups."
    base_url = "field-groups"
    required_settings = []
    default_settings = {}
    docs_view_name = "plugins:field_groups:docs"
    searchable_models = ["fieldgroupsexamplemodel"]


config = FieldGroupsConfig  # pylint:disable=invalid-name
