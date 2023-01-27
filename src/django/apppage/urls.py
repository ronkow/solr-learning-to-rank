from django.urls import path

from . import views

app_name = 'apppage'

urlpatterns = [
    path('grammar/', views.HomeView.as_view(), name = 'homeview'),
]
