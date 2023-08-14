from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
    """ Сериализатор модели пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(
                author=obj, follower=request.user
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор модели тега."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор вспомогательной модели
    ингредиента для рецепта с количеством.
    """
    id = serializers.ReadOnlyField(
        source='ingredients.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredients.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit',
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор создания ингредиента в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class RecipeListSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра рецептов."""
    tags = TagSerializer(
        many=True,
    )
    author = CustomUserSerializer()
    ingredients = IngredientAmountSerializer(
        source='am_ingredients',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'is_favorited',
            'is_in_shopping_cart', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('__all__',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                favorite_recipe=obj, author=request.user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Cart.objects.filter(
                recipe=obj, author=request.user
            ).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания рецепта."""
    author = CustomUserSerializer(
        read_only=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    ingredients = CreateIngredientInRecipeSerializer(
        many=True,
        required=True,
    )
    image = Base64ImageField(
        required=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

    def to_representation(self, instance):
        return RecipeListSerializer(instance).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)

        for ingredient in ingredients_data:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance.tags.clear()
        instance.tags.set(tags)

        instance.ingredients.clear()
        for ingredient in ingredients_data:
            IngredientAmount.objects.create(
                recipe=instance,
                ingredients=ingredient['id'],
                amount=ingredient['amount'],
            )

        instance.save()
        return instance


class RecipeShortListSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения короткого рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('__all__',)


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения списка подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeShortListSerializer(recipes, many=True,).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ('author', 'favorite_recipe',)

    def to_representation(self, instance):
        return RecipeShortListSerializer(instance.favorite_recipe).data


class CartSerializer(serializers.ModelSerializer):
    """ Сериализатор для добавления рецептов в список покупок."""

    class Meta:
        model = Cart
        fields = ('author', 'recipe',)

    def to_representation(self, instance):
        return RecipeShortListSerializer(instance.recipe).data
