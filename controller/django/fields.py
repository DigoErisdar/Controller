from controller.core.fields import CustomField


class AuthUser(CustomField):
    """Получает текущего пользователя из request"""
    __root__ = int
