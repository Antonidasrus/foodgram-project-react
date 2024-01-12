from rest_framework.permissions import IsAuthenticated

MAX_EMAIL_LENGTH = 254
MAX_USER_LENGTH = 100
MAX_PAGE_SIZE = 100
PAGE_SIZE = 6
DEFAULT_LIMIT = 100
MAX_TAG_COLOR_LENGTH = 7
MAX_NAME_SLUG_MEASUREMENT_UNIT_LENGTH = 200
MIN_TEXT_LENGTH = 2
MIN_HEX_LENGTH = 4
MIN_MEASUREMENT_UNIT_LENGTH = 1
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 1000
MIN_AMOUNT = 1
MAX_AMOUNT = 50000
MAX_LIMIT = 100

ARGUMENTS_FOR_ACTION_DECORATORS = {
    'post': {
        'methods': ('post',),
        'detail': True,
        'permission_classes': (IsAuthenticated,),
    },
    'get': {
        'detail': False,
        'permission_classes': (IsAuthenticated,),
    },
    'del': {
        'methods': ('delete',),
        'detail': True,
        'permission_classes': (IsAuthenticated,),
    },
}
