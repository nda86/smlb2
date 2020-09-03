# coding=utf-8
from api.utils import set_current_user
from rest_framework.authtoken.models import Token


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = None
        try:
            token = str(request.META.get('HTTP_AUTHORIZATION')).split(' ')[1]
            token_model = Token.objects.filter(key=token).first()
            if token_model:
                user = token_model.user
            # print(token)
        # если нет токена то берем юзера из заголовков запроса
        except Exception:
            user = getattr(request, 'user', None)
        set_current_user(user)
        response = self.get_response(request)
        return response
