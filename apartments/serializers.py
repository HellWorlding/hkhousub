from rest_framework import serializers

from .models import Apartment, Complex


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = [
            "id",
            "complex",
            "name",
            "area",
            "supply_count",
            "price",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ComplexSerializer(serializers.ModelSerializer):
    # 중첩 직렬화: 단지 조회 시 소속 아파트 목록을 함께 내려준다 (읽기 전용).
    apartments = ApartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Complex
        fields = ["id", "name", "region", "created_at", "apartments"]
        read_only_fields = ["id", "created_at"]


class CutlineSerializer(serializers.Serializer):
    """커트라인 응답 전용 DTO. 모델이 아닌 계산 결과를 담으므로 일반 Serializer 사용.

    (ModelSerializer는 DB 모델용, 이건 서비스 계산 결과용 → 스프링의 응답 전용 DTO)
    """

    apartment_id = serializers.UUIDField()
    apartment_name = serializers.CharField()
    supply_count = serializers.IntegerField()
    application_count = serializers.IntegerField()
    competition_rate = serializers.FloatField()
    status = serializers.CharField()
    cutline_score = serializers.IntegerField(allow_null=True)
