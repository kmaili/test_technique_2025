from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .kafka_producer import kafka_producer
from django.conf import settings
from .models import Measurement
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MeasurementSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_datetime
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def webhook(request):
    """
    Webhook endpoint for Shelly Pro 1PM
    Accepts GET (query params) and POST (JSON body)
    """
    data = {}

    # Handle POST
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Handle GET
    elif request.method == "GET":
        data = request.GET.dict()

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    required_fields = ["power", "voltage", "current", "energy"]
    for field in required_fields:
        if field not in data:
            return JsonResponse({"error": f"Missing field: {field}"}, status=400)

    data["timestamp"] = timezone.now()

    measurement = Measurement.objects.create(
        power=float(data["power"]),
        voltage=float(data["voltage"]),
        current=float(data["current"]),
        energy=float(data["energy"]),
        timestamp=data["timestamp"]
    )

    try:
        kafka_producer.send({
            "power": measurement.power,
            "voltage": measurement.voltage,
            "current": measurement.current,
            "energy": measurement.energy,
            "timestamp": measurement.timestamp.isoformat()
        })
    except Exception as e:
        logger.error("Kafka error:", e)

    return JsonResponse({"status": "success", "data": data})

def realtime_view(request):
    """
    Render a page showing the 10 latest measurements
    """
    latest_measurements = Measurement.objects.all()[:10]
    
    return render(request, "measurements/realtime_display.html", {
        "measurements": latest_measurements,
        "power_alert_threshold": settings.POWER_ALERT_THRESHOLD
    })


@api_view(['GET'])
def latest_measurements(request):
    """
    Returns the 10 latest measurements
    """
    latest = Measurement.objects.all()[:10]
    serializer = MeasurementSerializer(latest, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def measurements_list(request):
    """
    GET /api/measurements/?page=1&start=...&end=...
    Returns paginated measurements, optionally filtered by start/end datetime
    """
    queryset = Measurement.objects.all()
    
    start = request.GET.get("start")
    end = request.GET.get("end")

    if start:
        start_dt = parse_datetime(start)
        if start_dt:
            queryset = queryset.filter(timestamp__gte=start_dt)
    if end:
        end_dt = parse_datetime(end)
        if end_dt:
            queryset = queryset.filter(timestamp__lte=end_dt)
    
    queryset = queryset.order_by("-timestamp")
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = MeasurementSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)
