# Generated by Django 3.2.3 on 2023-08-10 12:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_auto_20230810_1147'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_recipe_user',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='user',
        ),
        migrations.AddField(
            model_name='favorite',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='author_fav', to='users.user', verbose_name='Подписчик на рецепт'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='favorite',
            name='favorite_recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipe', verbose_name='Избранный рецепт'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('author', 'favorite_recipe'), name='unique_favorite_recipes_author'),
        ),
    ]