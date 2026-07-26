from django.db import models

from common.models import BaseModel


class Application(BaseModel):
    """청약 (커머스의 Order 격). 회원이 특정 아파트에 넣는다.

    Apartment N:1, Member N:1 을 잇는 조인 성격의 엔티티.
    일반 주문과 달리 배정은 '선착순'이 아니라 '가점 랭킹'으로 결정된다.
    """

    # app 간 FK는 문자열 "앱라벨.모델명" 으로 참조 → 순환 import 방지 (pystagram 방식).
    apartment = models.ForeignKey(
        "apartments.Apartment", on_delete=models.CASCADE, related_name="applications"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="applications"
    )
    score = models.PositiveIntegerField()  # 청약 시점의 가점 스냅샷 (view에서 채움)

    class Meta:
        # 같은 회원이 같은 아파트에 중복 청약 불가. JPA @UniqueConstraint 와 동일.
        constraints = [
            models.UniqueConstraint(
                fields=["apartment", "member"],
                name="unique_application_per_member_apartment",
            )
        ]

    def __str__(self):
        return f"{self.member_id} → {self.apartment_id} ({self.score})"
