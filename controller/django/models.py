from typing import Optional, Any

from controller.core.models import Model
from controller.django.fields import AuthUser


class DjangoModelMixin(Model):
    """Позволяет принимать в себя request, чтобы спарсить данные с запроса"""
    _request: Optional[Any] = None

    def __init__(self, **kwargs):
        def update_data(items):
            assert getattr(items, 'get')
            for key in items:
                if key.endswith('[]'):
                    data[key.replace('[]', '')] = items.getlist(key)
                else:
                    data[key] = items.get(key)

        data = {}
        request = kwargs.pop('request', None)
        if request:
            items = request.GET if request.method == 'GET' else request.data
            update_data(items)
        # В первую очередь идут параметры с запроса
        # Кваргсами есть возможность переопределить поля
        data.update(kwargs)
        # Невозможно переопределить AuthUser
        if request:
            for key in self.get_list_for_auth_user():
                data[key] = request.user.id if request.user.is_authenticated else None
        super(DjangoModelMixin, self).__init__(**data)

    def get_list_for_auth_user(self):
        # Примитивно, но работает
        return list(
            filter(lambda item: self.__annotations__[item] in [AuthUser, Optional[AuthUser]],
                   self.__annotations__)
        )
