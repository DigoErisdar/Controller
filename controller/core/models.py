import re
from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel, BaseConfig

from controller.core.db import DataBase
from controller.core.functions import count


def log(func):
    def wrapper(self, *args, **kwargs):
        self.send_log(func, args, kwargs)
        response = func(self, *args, **kwargs)
        return response

    return wrapper


class Model(BaseModel):
    _db: DataBase
    _func_name: str = None

    class Config(BaseConfig):
        use_enum_values = True
        validate_all = True
        validate_assignment = True
        error_msg_templates = {
            'type_error.none.not_allowed': 'Поле не может быть пустым',
            'value_error.missing': "Поле обязательное",
            'value_error.const': "Заданное значение не входит в список разрешенных для этого поля"
        }

    def __str__(self):
        return f"{self.__class__.__name__}({super(Model, self).__str__()})"

    @property
    def sql_func(self):
        return f"{self.func_name}({','.join(map(DataBase.error_to_sql, self.dict().values()))})"

    @staticmethod
    def camel_to_snake(full_name):
        def to_snake(name):
            return re.sub(r'(?<!^)(?=[A-Z])', '_', name)

        return '.'.join(map(to_snake, full_name.split('.'))).lower()

    @property
    def func_name(self):
        return self._func_name or self.camel_to_snake(self.__class__.__qualname__)

    @staticmethod
    def catch_response(data: Any):
        """Обработка ответа"""
        return data

    def send_log(self, func, args, kwargs):
        now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        print(f'{now}: Вызов {self.func_name} {func.__name__}({args};{kwargs}) с параметрами: {self.dict()}')


class FunctionModel(Model):

    def __len__(self):
        return self.length()

    @log
    def get(self, limit: int = 1) -> Union[dict, list]:
        """Получение n элементов"""
        with self._db as db:
            return self.catch_response(
                db.function(*self.dict().values(), func_name=self.func_name, response_limit=limit))

    @log
    def all(self):
        """Получение всех элементов"""
        with self._db as db:
            return self.catch_response(db.function(*self.dict().values(), func_name=self.func_name, response_limit=-1))

    @log
    def length(self) -> int:
        """Получение количество строк"""
        with self._db as db:
            return db.function(*self.dict().values(),
                               func_name=self.func_name, response_limit=1,
                               aggregate=count()).get('count', 0)


class ProcedureModel(Model):
    @log
    def execute(self):
        """Выполнить"""
        with self._db as db:
            return self.catch_response(db.procedure(*self.dict().values(), func_name=self.func_name))
