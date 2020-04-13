from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

router = DefaultRouter()
router.register('courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    #path('courses_by_teacher/<int:user_id>/', CourseViewSet.as_view({"get": "courses_by_teacher"})),
]

#urlpatterns = router.urls
