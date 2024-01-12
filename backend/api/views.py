from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from api.serializers import RecipeReadSerializer
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticatedOrReadOnly
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Cart, FavoriteRecipe, Ingredient, Tag
from users.models import User

from core.constants import ARGUMENTS_FOR_ACTION_DECORATORS
from core.filters import IngredientFilter, RecipeFilter
from core.pagination import CartPagination, DefaultPagination
from core.permissions import IsAdminOrReadOnly
from core import services

from api.serializers import (UserSerializer, IngredientSerializer,
                             TagSerializer, WriteRecipeSerializer,
                             CartSerializer)


class UserViewSet(DjoserUserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = DefaultPagination

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('post'))
    def subscribe(self, request, id):
        return services.make_subscribe(
            request=request, user=request.user, author_id=id,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
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

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return services.get_flags(self.request)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return WriteRecipeSerializer

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('post'))
    def favorite(self, request, pk):
        return services.add_recipe_to_favorite_or_cart(
            model=FavoriteRecipe, user=request.user, id=pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return services.delete_recipe_from_favorite_or_cart(
            model=FavoriteRecipe, user=request.user, id=pk
        )

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('post'))
    def shopping_cart(self, request, pk):
        self.queryset = Cart.objects.all().order_by('-id',)
        self.pagination_class = CartPagination
        self.serializer_class = CartSerializer
        return services.add_recipe_to_favorite_or_cart(
            model=Cart, user=request.user, id=pk
        )

    @shopping_cart.mapping.delete
    def delete_recipe_from_favorite_or_cart(self, request, pk):
        return services.delete_recipe_from_favorite_or_cart(
            model=Cart, user=request.user, id=pk
        )

    @action(**ARGUMENTS_FOR_ACTION_DECORATORS.get('get'))
    def download_shopping_cart(self, request):
        return services.create_and_download_shopping_cart(request.user)
