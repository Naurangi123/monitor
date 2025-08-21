from rest_framework import views, generics, response, status
from django.db import transaction
from .models import Host, Snapshot, Process
from .serializers import IngestPayloadSerializer, HostSerializer, SnapshotSerializer
from core.auth import check_api_key

class IngestView(views.APIView):
    def post(self, request):
        check_api_key(request)
        s = IngestPayloadSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        with transaction.atomic():
            host, _ = Host.objects.get_or_create(hostname=data["hostname"])
            snap = Snapshot.objects.create(host=host, taken_at=data["snapshot_time"])
            processes = [
                Process(snapshot=snap, **p) for p in data["processes"]
            ]
            Process.objects.bulk_create(processes)

        return response.Response({"status": "ok", "snapshot_id": snap.id}, status=status.HTTP_201_CREATED)

class HostsListView(generics.ListAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class HostLatestSnapshotView(views.APIView):
    def get(self, request, hostname):
        try:
            host = Host.objects.get(hostname=hostname)
        except Host.DoesNotExist:
            return response.Response({"detail":"Host not found"}, status=404)
        snap = host.snapshot_set.order_by("-taken_at").first()
        if not snap:
            return response.Response({"detail":"No snapshots"}, status=404)
        return response.Response(SnapshotSerializer(snap).data)
