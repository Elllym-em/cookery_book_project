from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """ Модель тега."""
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингредиента."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления должно'
            'быть больше или равно 1 минуте.'
        ),)
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """ Модель ингредиента в рецепте."""
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='am_ingredients',
        verbose_name='Ингредиенты',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='am_ingredients',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(
            limit_value=1, message='Количество должно быть больше или равно 1.'
        ),)
    )

    def __str__(self):
        return f'{self.ingredients} входят в {self.recipe}'


class Favorite(models.Model):
    """ Модель избранных рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_fav',
        verbose_name='Подписчик на рецепт'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_fav_recipes_author',
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.author}'


class Cart(models.Model):
    """ Модель списка покупок."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors_shopping_cart',
        verbose_name='F'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_cart',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_recipes_author',
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.author}'
