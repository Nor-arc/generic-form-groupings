"""Django API urlpatterns declaration for field_groups app."""

from nautobot.apps.api import OrderedDefaultRouter

from field_groups.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("field-groups-example-models", views.FieldGroupsExampleModelViewSet)

app_name = "field_groups-api"
urlpatterns = router.urls
