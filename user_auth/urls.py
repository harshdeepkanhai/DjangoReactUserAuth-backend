from django.urls import path
from .views import current_user, CreateUserView

urlpatterns = [
    path('current_user/', current_user),
    path('signup/', CreateUserView.as_view())
]