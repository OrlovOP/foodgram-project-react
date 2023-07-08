from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, IngredientViewSet, TagViewSet, MyUserViewSet

router = DefaultRouter()

router.register(r'^recipes', RecipeViewSet, basename='recipes')
router.register(r'^ingredients', IngredientViewSet, basename='ingredients')
router.register(r'^tags', TagViewSet, basename='tags')
router.register(r'users', MyUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
