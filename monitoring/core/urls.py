from django.urls import path
from .views import *
urlpatterns = [
    path("ingest/", IngestView.as_view(),name='ingest'),
    path("hosts/", HostsListView.as_view(),name='hosts'),
    path("hosts/<str:hostname>/latest/", HostLatestSnapshotView.as_view(),name='host_latest_snapshot'),
]
