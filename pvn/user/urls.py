from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    index,
    RegistrationView,
    LoginView,
)

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('', index, name='home'),
]
