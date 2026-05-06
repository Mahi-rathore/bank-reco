from django.urls import path
from .views import recommend, ask

urlpatterns = [
    path('recommend/', recommend),
    path('ask/', ask),
]