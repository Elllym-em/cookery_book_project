# Generated by Django 3.2.3 on 2023-08-11 09:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0004_auto_20230810_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors_shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='F')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_in_cart', to='recipes.recipe', verbose_name='Избранный рецепт')),
            ],
            options={
                'verbose_name_plural': 'Списки покупок',
            },
        ),
        migrations.AddConstraint(
            model_name='cart',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_recipes_author'),
        ),
    ]