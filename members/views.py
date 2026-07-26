from rest_framework import viewsets

from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet):
    """회원 CRUD. ModelViewSet = list/create/retrieve/update/destroy를 한 번에 제공.

    스프링이라면 @RestController + @GetMapping/@PostMapping ... 5개를 짜야 하는데,
    DRF는 ViewSet 하나로 REST CRUD 전체를 자동 제공한다.
    """

    queryset = Member.objects.all().order_by("-score")
    serializer_class = MemberSerializer
