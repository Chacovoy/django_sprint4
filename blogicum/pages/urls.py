from django.urls import path
from django.views.generic import TemplateView as Tv


app_name = "pages"

urlpatterns = [
    path("about/", Tv.as_view(template_name="pages/about.html"), name="about"),
    path("rules/", Tv.as_view(template_name="pages/rules.html"), name="rules"),
]
