from rest_framework import serializers

from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    """회원 DTO. 스프링의 DTO + Jackson 매핑에 해당.

    ModelSerializer = 모델을 보고 필드를 자동 생성 (JPA 엔티티 → DTO 자동 매핑 느낌).
    """

    class Meta:
        model = Member
        fields = ["id", "name", "score", "created_at"]
        read_only_fields = ["id", "created_at"]
