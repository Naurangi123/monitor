from rest_framework import serializers
from .models import *


class ProcessIngestSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    ppid = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    cmdline = serializers.JSONField(required=False, allow_null=True)
    cpu_percent = serializers.FloatField(required=False, allow_null=True)
    memory_rss = serializers.IntegerField(required=False, allow_null=True)


class IngestPayloadSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    snapshot_time = serializers.DateTimeField()
    processes = ProcessIngestSerializer(many=True)
    

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'

class SnapshotSerializer(serializers.ModelSerializer):
    processes = ProcessSerializer(many=True, read_only=True)
    class Meta:
        model = Snapshot
        fields = '__all__'

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'