"""샘플 데이터 주입 커맨드.

실행: python manage.py seed
스프링의 data.sql / CommandLineRunner 초기 데이터 주입과 같은 역할.
멱등하게 만들기 위해 기존 도메인 데이터를 먼저 지운다.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apartments.models import Apartment, Complex
from applications.models import Application
from members.models import Member


class Command(BaseCommand):
    help = "청약 서비스 샘플 데이터를 생성한다."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1) 초기화 (FK 역순으로 삭제)
        Application.objects.all().delete()
        Apartment.objects.all().delete()
        Complex.objects.all().delete()
        Member.objects.all().delete()

        # 2) 단지 + 아파트
        gangnam = Complex.objects.create(name="래미안 강남", region="서울 강남구")
        apt_84 = Apartment.objects.create(
            complex=gangnam, name="84A", area=84.97, supply_count=3, price=1_200_000_000
        )
        apt_59 = Apartment.objects.create(
            complex=gangnam, name="59B", area=59.94, supply_count=10, price=900_000_000
        )

        # 3) 회원 (가점 다양하게)
        members_data = [
            ("김철수", 70),
            ("이영희", 65),
            ("박민수", 62),
            ("최지우", 55),
            ("정해인", 40),
        ]
        members = [
            Member.objects.create(name=name, score=score)
            for name, score in members_data
        ]

        self.stdout.write(
            self.style.SUCCESS(
                f"완료 ✅  단지 1, 아파트 2(84A/59B), 회원 {len(members)}명 생성.\n"
                f"→ 84A 공급 {apt_84.supply_count}세대 / 59B 공급 {apt_59.supply_count}세대\n"
                f"→ 청약(Application)은 API로 넣어 커트라인을 확인하세요."
            )
        )
