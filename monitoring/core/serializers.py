from rest_framework import serializers
from .models import *



class IngestPayloadSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    snapshot_time = serializers.DateTimeField()
    processes = ProcessIngestSerializer(many=True)
    


class SnapshotSerializer(serializers.ModelSerializer):
    processes = ProcessSerializer(many=True, read_only=True)
    class Meta:
        model = Snapshot
        fields = '__all__'

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'