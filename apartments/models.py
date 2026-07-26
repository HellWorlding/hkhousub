from django.core.validators import MinValueValidator
from django.db import models

from common.models import BaseModel


class Complex(BaseModel):
    """단지 (커머스의 Company/Brand 격). 여러 아파트를 보유한다."""

    name = models.CharField(max_length=100)       # 단지명 (예: "래미안 강남")
    region = models.CharField(max_length=100)     # 지역 (예: "서울 강남구")

    def __str__(self):
        return self.name


class Apartment(BaseModel):
    """아파트/주택형 (커머스의 Product 격). 단지에 속한다 (N:1)."""

    # ForeignKey = JPA @ManyToOne. on_delete=CASCADE → 단지 삭제 시 아파트도 삭제.
    # related_name="apartments" → 역참조: complex.apartments.all()
    complex = models.ForeignKey(
        Complex, on_delete=models.CASCADE, related_name="apartments"
    )
    name = models.CharField(max_length=50)        # 주택형 (예: "84A")
    area = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )  # 전용면적(㎡)
    supply_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )  # 공급 세대수 = 재고. 커트라인 계산의 N.
    price = models.BigIntegerField(null=True, blank=True)  # 분양가(원)

    def __str__(self):
        return f"{self.complex.name} {self.name}"
