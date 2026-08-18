from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Self Checkout Admin"
admin.site.site_title = "Self Checkout"
admin.site.index_title = "Store Management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("payments/", include("payments.urls")),
    path("", include("billing.urls")),
]