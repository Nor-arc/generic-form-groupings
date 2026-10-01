"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:field_groups:fieldgroupsexamplemodel_list",
        name="Field Groups",
        permissions=["field_groups.view_fieldgroupsexamplemodel"],
        buttons=(
            NavMenuAddButton(
                link="plugins:field_groups:fieldgroupsexamplemodel_add",
                permissions=["field_groups.add_fieldgroupsexamplemodel"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="Field Groups", items=tuple(items)),),
    ),
)
