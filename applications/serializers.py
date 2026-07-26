from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from . import services
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "apartment", "member", "score", "created_at"]
        # score는 요청으로 받지 않고 서버가 회원 가점을 복사 (read_only).
        read_only_fields = ["id", "score", "created_at"]
        # 같은 (아파트, 회원) 중복 청약 시 500이 아니라 400을 주도록 검증 추가.
        validators = [
            UniqueTogetherValidator(
                queryset=Application.objects.all(),
                fields=["apartment", "member"],
                message="이미 이 아파트에 청약한 회원입니다.",
            )
        ]

    def create(self, validated_data):
        # 실제 생성 로직은 서비스 계층에 위임 (view→serializer→service).
        return services.apply(
            apartment=validated_data["apartment"],
            member=validated_data["member"],
        )
