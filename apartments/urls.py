from rest_framework.routers import SimpleRouter

from .views import ApartmentViewSet, ComplexViewSet

router = SimpleRouter()
router.register("complexes", ComplexViewSet)
router.register("apartments", ApartmentViewSet)  # cutline 액션은 라우터가 자동 등록

urlpatterns = router.urls
