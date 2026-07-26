from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import Apartment, Complex
from .serializers import ApartmentSerializer, ComplexSerializer, CutlineSerializer


class ComplexViewSet(viewsets.ModelViewSet):
    queryset = Complex.objects.all().order_by("-created_at")
    serializer_class = ComplexSerializer


class ApartmentViewSet(viewsets.ModelViewSet):
    # select_related: FK(complex)를 JOIN으로 미리 가져와 N+1 쿼리 방지 (JPA fetch join).
    queryset = Apartment.objects.select_related("complex").all()
    serializer_class = ApartmentSerializer

    @action(detail=True, methods=["get"])
    def cutline(self, request, pk=None):
        """GET /api/apartments/{id}/cutline/ — 커트라인 조회.

        @action(detail=True) = 단건 리소스에 붙는 커스텀 엔드포인트.
        스프링의 @GetMapping("/apartments/{id}/cutline") 커스텀 메서드와 동일.
        """
        apartment = self.get_object()
        data = services.calculate_cutline(apartment)
        return Response(CutlineSerializer(data).data)
