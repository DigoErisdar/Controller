from datetime import datetime
from typing import List

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
    """Неизменяемое значение"""

    @classmethod
    def validate(cls, value, values, config, field):
        return field.default


class FormatDate(CustomField):
    """Поле для форматирования даты из строки"""
    _input_format: List[str]
    _output_format: str
    _ERROR = "Не правильный формат даты"

    @classmethod
    def validate(cls, value, values, config, field):
        if not value:
            return None
        for frmt in cls._input_format:
            try:
                dt = datetime.strptime(value, frmt)
            except Exception as e:
                pass
            else:
                try:
                    return dt.strftime(cls._output_format)
                except Exception:
                    raise ValueError(cls._ERROR)
        raise ValueError(cls._ERROR)
