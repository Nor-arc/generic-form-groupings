"""Django urlpatterns declaration for field_groups app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter


from field_groups import views


app_name = "field_groups"
router = NautobotUIViewSetRouter()

# The standard is for the route to be the hyphenated version of the model class name plural.
# for example, ExampleModel would be example-models.
router.register("field-groups-example-models", views.FieldGroupsExampleModelUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("field_groups/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
