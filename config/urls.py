from django.contrib import admin
from django.urls import path

from analyzer.views import upload_csv


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", upload_csv, name="upload_csv"),
]