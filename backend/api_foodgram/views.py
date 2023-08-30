from django.db.models import Sum
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from users.models import Follow, User
from .filters import IngredientsFilter, RecipeFilters
from .paginations import CustomPagination
from .permissions import (IsAdminOrReadOnly, IsAuthor,
                          IsAuthorOrAdminOrReadOnly, IsAuthForUsers)
from .serializers import (CartSerializer, CustomUserSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    """ Viewset для пользователей."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthForUsers,)
    pagination_class = CustomPagination

    @action(
        detail=False, methods=['get'], url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(
            serializer.data, status=status.HTTP_200_OK,
        )


class TagViewSet(viewsets.ModelViewSet):
    """
    Viewset для получения списка тегов
    или конкретного тега любым пользователем.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Viewset для получения списка ингредиентов
    или конкретного ингредиента любым пользователем.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)
    pagination_class = None


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

    def perform_create_action(
        self, request, recipe, model, serializer, errors_message
    ):
        model_object, created = model.objects.get_or_create(
            recipe=recipe,
            author=request.user
        )
        if created:
            serializer = serializer(model_object)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED,
            )
        return Response(
            {'errors': errors_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def perform_delete_action(
        self, request, recipe, model, errors_message
    ):
        model_object = model.objects.filter(recipe=recipe)
        if model_object.exists():
            model_object.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {'errors': errors_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        permission_classes=[IsAuthor]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            return self.perform_create_action(
                request, recipe, Favorite,
                FavoriteSerializer,
                'Рецепт уже добавлен в избранное',
            )

        return self.perform_delete_action(
            request, recipe, Favorite,
            'Рецепт не был добавлен в избранное',
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        permission_classes=[IsAuthor]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            return self.perform_create_action(
                request, recipe, Cart,
                CartSerializer,
                'Рецепт уже добавлен в список покупок',
            )

        return self.perform_delete_action(
            request, recipe, Cart,
            'Рецепт не был добавлен в список покупок',
        )

    @action(
        detail=False, methods=['get'], url_path='download_shopping_cart',
        permission_classes=[IsAuthor]
    )
    def download_shopping_cart(self, request):
        pdfmetrics.registerFont(TTFont(
            'Lato-Light', f'{settings.BASE_DIR}/data/lato-light.ttf', 'UTF-8'
        ))

        ingredients = IngredientAmount.objects.filter(
            recipe__recipe_in_cart__author=request.user
        ).values_list(
            'ingredients__name', 'ingredients__measurement_unit',
        ).annotate(amount=Sum('amount'))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_cart.pdf"')
        page = canvas.Canvas(response)
        page.setFont("Lato-Light", 15)

        indent = 800
        for _, ingredient in enumerate(ingredients, start=1):
            page.drawString(
                50, indent, (f'{ingredient[0]}: '
                             f'{ingredient[2]} '
                             f'{ingredient[1]}')
            )
            indent -= 20

        page.showPage()
        page.save()
        return response


class FollowListView(generics.ListAPIView):
    """View-класс для получения списка подписок."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)


class FollowCreateView(APIView):
    """ View-класс для создания и удаления подписки."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))

        if Follow.objects.filter(
            author=author,
            follower=request.user
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FollowSerializer(
            data=request.data,
            context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author, follower=self.request.user)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED,
        )

    def delete(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))
        subscribe = Follow.objects.filter(author=author, follower=request.user)
        if subscribe.exists():
            subscribe.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {'errors': 'Вы не были подписаны на этого автора'},
            status=status.HTTP_400_BAD_REQUEST,
        )
