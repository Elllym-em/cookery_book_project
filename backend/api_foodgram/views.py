from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from users.models import Follow, User
from .filters import RecipeFilters
from .mixins import CreateListDestroyViewSet
from .paginations import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthor, IsAuthorOrAdminOrReadOnly
from .serializers import (CartSerializer, CustomUserSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, TagSerializer)


class UserList(generics.ListAPIView):
    """
    View-класс для получения списка
    пользователей для неавторизованного пользователя.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination


class TagViewSet(viewsets.ModelViewSet):
    """
    Viewset для получения списка тегов
    или конкретного тега любым пользователем.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Viewset для получения списка ингредиентов
    или конкретного ингредиента любым пользователем.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Viewset для рецептов, включая избранное и список покупок."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

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

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        permission_classes=[IsAuthor]
    )
    def favorite(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                favorite_recipe=recipe,
                author=request.user,
            )
            if created:
                serializer = FavoriteSerializer(favorite)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED,
                )
            return Response(
                {'errors': 'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(favorite_recipe=recipe).exists()
            if favorite:
                Favorite.objects.get(
                    favorite_recipe=recipe,
                    author=request.user,
                ).delete()
                return Response(
                    {'message': 'Рецепт успешно удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT,
                    )
            return Response(
                {'errors': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        permission_classes=[IsAuthor]
    )
    def shopping_cart(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)

        if request.method == 'POST':
            shopping_cart, created = Cart.objects.get_or_create(
                recipe=recipe,
                author=request.user,
            )
            if created:
                serializer = CartSerializer(shopping_cart)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED,
                )
            return Response(
                {'errors': 'Рецепт уже добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'DELETE':
            in_shopping_cart = Cart.objects.filter(recipe=recipe).exists()
            if in_shopping_cart:
                Cart.objects.get(
                    recipe=recipe,
                    author=request.user,
                ).delete()
                return Response(
                    {'message': 'Рецепт успешно удален из списка покупок'},
                    status=status.HTTP_204_NO_CONTENT,
                    )
            return Response(
                {'errors': 'Рецепт не был добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False, methods=['get'], url_path='download_shopping_cart',
        permission_classes=[IsAuthor]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__recipe_in_cart__author=request.user
        ).values_list(
            'ingredients__name', 'ingredients__measurement_unit',
        ).annotate(amount=Sum('amount'))

        response = HttpResponse(ingredients, 'Content-Type:text/plane')
        response['Content-Disposition'] = ('attachment;'
                                           'filename=shopping_cart.txt')
        return response


class FollowViewSet(CreateListDestroyViewSet):
    """ Viewset для реализации функционала подписок."""
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.request.user.follower.all()

    @action(
            detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(author__follower=request.user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        author = User.objects.get(pk=pk)

        if request.method == 'POST':
            subscribe, created = Follow.objects.get_or_create(
                author=author,
                follower=request.user,
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
            subscribe = Follow.objects.filter(author=author).exists()
            if subscribe:
                Follow.objects.get(
                    author=author, follower=request.user
                ).delete()
                return Response(
                    {'message': 'Успешная отписка'},
                    status=status.HTTP_204_NO_CONTENT,
                    )
            return Response(
                {'errors': 'Вы не были подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
