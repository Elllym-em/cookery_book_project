from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, FollowListView, FollowCreateView,
                    RecipeViewSet, TagViewSet, UserViewSet)

router_api = routers.DefaultRouter()

router_api.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_api.register(r'recipes', RecipeViewSet, basename='recipes')
router_api.register(r'tags', TagViewSet, basename='tags')
router_api.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('users/subscriptions/', FollowListView.as_view()),
    path('users/<int:user_id>/subscribe/', FollowCreateView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_api.urls)),
]