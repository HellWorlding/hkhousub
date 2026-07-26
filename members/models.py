from django.core.validators import MaxValueValidator
from django.db import models

from common.models import BaseModel


class Member(BaseModel):
    """회원 (커머스의 User 격). 청약의 주체."""

    name = models.CharField(max_length=50)
    score = models.PositiveIntegerField(
        validators=[MaxValueValidator(84)]
    )  # 청약가점 (0~84). PositiveIntegerField 라 음수 불가.

    def __str__(self):
        return f"{self.name}({self.score})"
