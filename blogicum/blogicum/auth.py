from django.contrib.auth.forms import UserCreationForm
from django.urls import path, reverse_lazy, include
from django.views.generic import CreateView

urlpatterns = [
    path(
        'registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('', include('django.contrib.auth.urls')),
]
