from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow, User
from .mixins import CreateListDestroyViewSet
from .serializers import (
    CustomUserSerializer, FollowSerializer,
    IngredientSerializer, RecipeListSerializer, RecipeCreateSerializer,
    TagSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly, IsAuthorOrReadOnly


class UserList(generics.ListAPIView):
    """
    View-класс для получения списка
    пользователей для неавторизованного пользователя.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    """
    Viewset для получения списка тегов
    или конкретного тега любым пользователем.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Viewset для получения списка ингредиентов
    или конкретного ингредиента любым пользователем.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Viewset для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'partial_update' or self.action == 'destroy':
            return (IsAuthorOrAdminOrReadOnly(),)
        elif self.action == 'update':
            return (IsAdminOrReadOnly(),)
        return super().get_permissions()


class FollowViewSet(CreateListDestroyViewSet):
    """ Viewset для реализации функционала подписок."""

    def get_queryset(self):
        return self.request.user.follower.all()

    @action(
            detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        follower = request.user
        subscriptions = User.objects.filter(author__follower=follower)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        follower = request.user
        author = User.objects.get(pk=pk)

        if request.method == 'POST':
            subscribe, created = Follow.objects.get_or_create(
                author=author,
                follower=follower,
            )
            if created:
                serializer = FollowSerializer(subscribe.author)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED,
                )
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'DELETE':
            try:
                subscribe = Follow.objects.get(
                    author=author, follower=follower
                )
                subscribe.delete()
                return Response(
                    {'message': 'Успешная отписка'},
                    status=status.HTTP_204_NO_CONTENT,
                    )
            except Follow.DoesNotExist:
                Response(
                    {'errors': 'Вы не были подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
