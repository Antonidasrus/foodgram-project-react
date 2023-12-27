from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticatedOrReadOnly
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Cart, FavoriteRecipe, Ingredient, Recipe, Tag
from users.models import User

from core.constants import ARGUMENTS_FOR_ACTION_DECORATORS
from core.filters import IngredientFilter, RecipeFilter
from core.pagination import CartPagination, CustomPagination
from core.permissions import IsAdminOrReadOnly
from core import services

from api.serializers import (DjoserUserSerializer, IngredientSerializer,
                             RecipeReadSerializer, TagSerializer,
                             WriteRecipeSerializer, CartSerializer)


class DjoserUserViewSet(UserViewSet):
    """Наследованный джосер вьюсет"""

    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    pagination_class = CustomPagination

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('post_del'))
    def subscribe(self, request, id):
        if request.method == 'POST':
            return services.make_subscribe(
                request=request, user=request.user, author_id=id,
            )
        return services.unsubscribe(
            user=request.user, author_id=id
        )

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('get'))
    def subscriptions(self, request):
        return (
            self.get_paginated_response(
                services.get_subscription_serializer(
                    request=request,
                    pages=self.paginate_queryset(
                        services.get_author_in_subscription(user=request.user)
                    )
                ).data
            )
        )


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для отображения рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return WriteRecipeSerializer

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('post_del'))
    def favorite(self, request, pk):
        if request.method == 'POST':
            return services.add_recipe_to_favorite_or_cart(
                model=FavoriteRecipe, user=request.user, id=pk
            )
        return services.delete_recipe_from_favorite_or_cart(
            model=FavoriteRecipe, user=request.user, id=pk
        )

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('post_del'))
    def shopping_cart(self, request, pk):
        self.queryset = Cart.objects.all().order_by('-id',)
        self.pagination_class = CartPagination
        self.serializer_class = CartSerializer
        if request.method == 'POST':
            return services.add_recipe_to_favorite_or_cart(
                model=Cart, user=request.user, id=pk
            )
        return services.delete_recipe_from_favorite_or_cart(
            model=Cart, user=request.user, id=pk
        )

    def cart_text(self, user, ingredients, date):
        text = (
            f'Здравствуйте, {user.first_name}!\n\n'
            'Вот ваш список покупок на сегодня.\n\n'
            'Нужно купить:\n\n'
        )
        text += '\n'.join([
            f' - {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["in_shopping_cart_ingredient_amount"]}'
            for ingredient in ingredients
        ])
        text += '\n\nFoodgram.'
        return text

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('get'))
    def download_shopping_cart(self, request):
        self.queryset = Cart.objects.all().order_by('-id',)
        self.serializer_class = CartSerializer
        self.pagination_class = CartPagination
        return services.create_and_download_shopping_cart(request.user)
