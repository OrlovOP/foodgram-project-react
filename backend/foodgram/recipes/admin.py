from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, Cart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = 'нет значения'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'нет значения'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'text', 'get_ingredients',)
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = 'нет данных'
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        '''Вывожу ингредиенты.'''

        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.ingredient_list.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    empty_value_display = 'нет данных'


@admin.register(Cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    empty_value_display = 'нет данных'
