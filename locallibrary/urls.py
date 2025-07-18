from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),  # Include the catalog app's URLs
    path('accounts/', include('django.contrib.auth.urls')),  # For login/logout
]
