from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter


from recipes.models import Recipe


class RecipeFilters(filters.FilterSet):
    """ Фильтрация для рецептов."""
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='get_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='get_is_in_shopping_cart',
    )
    author = filters.CharFilter(
        field_name='author',
    )
    tags = filters.CharFilter(
        field_name='tags',
        method='get_tags',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
        distinct = True

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__author=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_in_cart__author=self.request.user
            )
        return queryset

    def get_tags(self, queryset, name, value):
        value = self.request.query_params.getlist('tags')
        if value:
            return queryset.filter(tags__slug__in=value).distinct()
        return queryset


class IngredientsFilter(SearchFilter):
    search_param = 'name'
