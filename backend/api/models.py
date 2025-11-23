from django.db import models
from django.contrib.auth.models import User  # Import User

class FileUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Add this line
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_count = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temperature = models.FloatField(default=0.0)

    def __str__(self):
        return f"Upload {self.id} - {self.uploaded_at}"

class Equipment(models.Model):
    upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=100)
    eq_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
