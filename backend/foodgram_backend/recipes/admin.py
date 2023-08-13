from django.contrib import admin

from .models import Cart, Favorite, Ingredient, IngredientAmount, Recipe, Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = [IngredientAmountInline]
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientAmountInline]
    list_display = (
        'id',
        'name',
        'author',
        'pub_date',
    )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')


@admin.register(Tag)
class TadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'favorite_recipe',
    )
    search_fields = ('author', 'favorite_recipe',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'recipe',
    )
    search_fields = ('author', 'recipe',)
