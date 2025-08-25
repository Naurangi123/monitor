from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    os = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.hostname

class Snapshot(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    taken_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    def __str__(self):
        return f"Snapshot of {self.host} at {self.taken_at}"

class Process(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name='processes')
    name = models.CharField(max_length=255)
    pid = models.IntegerField()
    ppid = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True)
    cmdline = models.TextField(blank=True)
    cpu_percent = models.FloatField(null=True, blank=True)
    memory_rss = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    def __str__(self):
        return f"Process {self.name} (PID: {self.pid}) on {self.snapshot.host}"
