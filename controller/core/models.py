import re
from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel, BaseConfig

from controller.core.db import DataBase
from controller.core.functions import count


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

    @staticmethod
    def send_log(action: dict, func_name: str, data: dict):
        current_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        action_string = f"{action.get('function')}({action.get('limit') or ''})"
        print(f"{current_date}: {action_string} {func_name} с {data}")


class FunctionModel(Model):

    def __len__(self):
        return self.length()

    def get(self, limit: int = 1) -> Union[dict, list]:
        """Получение n элементов"""
        self.send_log({'function': 'get', 'limit': limit}, self.func_name, self.dict())
        with self._db as db:
            return self.catch_response(
                db.function(*self.dict().values(), func_name=self.func_name, response_limit=limit))

    def all(self):
        """Получение всех элементов"""
        self.send_log({'function': 'all'}, self.func_name, self.dict())
        with self._db as db:
            return self.catch_response(db.function(*self.dict().values(), func_name=self.func_name, response_limit=-1))

    def length(self) -> int:
        """Получение количество строк"""
        self.send_log({'function': 'length'}, self.func_name, self.dict())
        with self._db as db:
            return db.function(*self.dict().values(),
                               func_name=self.func_name, response_limit=1,
                               aggregate=count()).get('count', 0)


class ProcedureModel(Model):
    def execute(self):
        """Выполнить"""
        self.send_log({'function': 'execute'}, self.func_name, self.dict())
        with self._db as db:
            return self.catch_response(db.procedure(*self.dict().values(), func_name=self.func_name))
