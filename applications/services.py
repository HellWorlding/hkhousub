"""청약 관련 비즈니스 로직 (스프링의 @Service)."""

from .models import Application


def apply(apartment, member):
    """청약을 생성한다. 청약 시점의 회원 가점을 스냅샷으로 복사한다.

    회원 가점이 나중에 바뀌어도, 이 청약은 당시 점수로 커트라인에 반영되어야 하므로
    member.score를 Application.score에 복사해 저장한다 (주문 시점 가격 복사 패턴).
    """
    return Application.objects.create(
        apartment=apartment,
        member=member,
        score=member.score,
    )
