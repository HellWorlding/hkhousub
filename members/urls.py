from rest_framework.routers import SimpleRouter

from .views import MemberViewSet

# Router = ViewSet을 URL에 자동 매핑 (스프링의 @RequestMapping 라우팅을 자동화).
# members/ → list·create, members/{id}/ → retrieve·update·destroy
router = SimpleRouter()
router.register("members", MemberViewSet)

urlpatterns = router.urls
