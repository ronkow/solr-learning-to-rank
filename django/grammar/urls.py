from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.generic.base import TemplateView


urlpatterns = [
    path('admin/',
        admin.site.urls),

    path('',
        include('apppage.urls')),

    path('quiz/',
        include('appquiz.urls')),

    path('search/',
        include('appsearch.urls')),

    path('accounts/',
        include('allauth.urls')),

    url(r'^solr/',
        include('haystack.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
