from rest_framework import serializers
from .models import *

class ProcessIngestSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    ppid = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255, allow_blank=True)
    status = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cmdline = serializers.CharField(required=False, allow_blank=True)
    cpu_percent = serializers.FloatField(required=False, allow_null=True)
    memory_rss = serializers.FloatField(required=False, allow_null=True)

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'

class IngestPayloadSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    snapshot_time = serializers.DateTimeField()
    system = serializers.DictField(required=False, allow_null=True)
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