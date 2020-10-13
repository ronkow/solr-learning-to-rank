from django.urls import path

from . import views

app_name = 'apppage'

urlpatterns = [
    path('grammar/',
        views.HomeView.as_view(),
        name = 'homeview'),

    path('about/',
        views.AboutView.as_view(),
        name = 'aboutview'),

    path('contact/',
        views.ContactView,
        name = 'contactview'),

    path('contact/success/',
        views.SuccessView,
        name = 'successview'),


    path('model/',
        views.ModelView.as_view(),
        name = 'modelview'),

    path('result/',
        views.ResultView.as_view(),
        name = 'resultview'),

    path('profile/',
        views.ProfileView.as_view(),
        name = 'profileview'),

    path('settings/',
        views.SettingsView.as_view(),
        name = 'settingsview'),
]
