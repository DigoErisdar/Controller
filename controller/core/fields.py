from pydantic import BaseModel


class CustomField(BaseModel):
    """Базовый класс для кастомных типов данных"""

    @classmethod
    def get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, values, config, field):
        """Обязательная функция для валидации"""
        return value


class Const(CustomField):

    @classmethod
    def validate(cls, value, values, config, field):
        return field.default
