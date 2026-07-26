import uuid

from django.db import models


class BaseModel(models.Model):
    """모든 엔티티 공통 필드. JPA의 @MappedSuperclass 에 해당.

    - id: UUID PK (uuid4 자동 생성)
    - created_at: 생성 시각 (INSERT 시 자동)
    abstract=True → 이 자체론 테이블이 안 생기고, 상속한 모델에만 컬럼이 붙는다.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
