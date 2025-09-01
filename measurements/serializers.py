from rest_framework import serializers
from .models import Measurement

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['power', 'voltage', 'current', 'energy', 'timestamp']
        read_only_fields = ['timestamp']