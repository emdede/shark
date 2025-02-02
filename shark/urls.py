"""
URL configuration for shark project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(
        "admin/billing/", include("shark.billing.admin_urls", namespace="billing_admin")
    ),
    path("admin/sepa/", include("shark.sepa.admin_urls", namespace="sepa_admin")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("admin_tools/", include("admin_tools.urls")),
    path("accounting/", include("shark.accounting.urls", namespace="accounting")),
    path("api/", include("shark.api_urls", namespace="api")),
    path("issue/", include("shark.issue.urls", namespace="issue")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
