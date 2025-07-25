from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

handler404 = "pages.views.custom_404"
# handler500 = "pages.views.custom_500"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls", namespace="pages")),  # Main page URL
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chat.urls")),
    path("patients/", include("patients.urls")),
    path("doctor/", include("doctor.urls")),
    path('api1/', include("api1.urls")),
    path('api2/', include('api2.urls')),
    path('api3/', include('api3.urls')),
    path('api4/', include("api4.urls")),
    path('api5/', include("api5.urls")),
    path('api6/', include("api6.urls")),
]

# Serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)