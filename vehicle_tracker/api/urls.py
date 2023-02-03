from django.contrib import admin
from django.urls import path,include
from .views import DownloadCsvVehicleTrails
urlpatterns = [
    path('download/csv/', DownloadCsvVehicleTrails.as_view()),
]
