from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
