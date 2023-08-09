from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet
from rest_framework.routers import DefaultRouter

from django.urls import include, path

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
