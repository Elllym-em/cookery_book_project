from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, FollowViewSet,
                    RecipeViewSet, TagViewSet, UserList)

router_api = routers.DefaultRouter()

router_api.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_api.register(r'recipes', RecipeViewSet, basename='recipes')
router_api.register(r'tags', TagViewSet, basename='tags')
router_api.register(r'users', FollowViewSet, basename='users')


urlpatterns = [
    path('users/', UserList.as_view()),
    path('', include(router_api.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
