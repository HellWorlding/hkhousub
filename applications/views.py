from rest_framework import viewsets

from .models import Application
from .serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = (
        Application.objects.select_related("apartment", "member")
        .order_by("-created_at")
    )
    serializer_class = ApplicationSerializer
