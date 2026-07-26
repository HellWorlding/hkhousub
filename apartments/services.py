"""아파트 관련 비즈니스 로직 (스프링의 @Service).

커트라인/경쟁률 계산처럼 view가 알 필요 없는 도메인 규칙을 여기 모은다.
"""


def calculate_cutline(apartment):
    """공급 세대수(N)와 청약 가점을 바탕으로 커트라인·경쟁률을 계산한다.

    - 청약을 가점 내림차순(동점이면 먼저 청약한 순)으로 정렬
    - 지원자 수 C >= N  → 커트라인 = N등의 가점, 상태 '마감'
    - C < N            → 커트라인 없음(None), 상태 '미달'
    - 경쟁률 = C / N (소수 둘째 자리 반올림)
    """
    applications = apartment.applications.order_by("-score", "created_at")
    count = applications.count()
    n = apartment.supply_count

    if count >= n:
        cutline_score = applications[n - 1].score  # N번째(0-index n-1) 지원자의 가점
        status = "마감"
    else:
        cutline_score = None
        status = "미달"

    return {
        "apartment_id": apartment.id,
        "apartment_name": apartment.name,
        "supply_count": n,
        "application_count": count,
        "competition_rate": round(count / n, 2),
        "status": status,
        "cutline_score": cutline_score,
    }
