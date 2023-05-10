from abc import ABCMeta, ABC

import psycopg2
from psycopg2 import DatabaseError


class AbstractDataBase(ABC, metaclass=ABCMeta):
    param_prefix = ''
    is_named_parameters = False

    def __query(self, callback, response_limit: int):
        """Выполнение запроса по получению"""

        def to_dict(item):
            if item:
                return dict(zip(columns, item))
            return {}

        with self.conn.cursor() as cursor:
            callback(cursor)
            columns = [col.name for col in cursor.description or []]
            if response_limit == 1:
                try:
                    response = to_dict(cursor.fetchone())
                except Exception:
                    return None
            elif response_limit <= 0:
                response = list(map(to_dict, cursor.fetchall()))
            else:
                response = list(map(to_dict, cursor.fetchmany(response_limit)))
            return response

    @staticmethod
    def error_to_sql(value):
        if value is None:
            return 'null'
        if not isinstance(value, str):
            return str(value)
        return f"'{value}'"

    @staticmethod
    def func_name_with_attrs_to_sql(func_name: str, *args):
        return f"{func_name}({','.join(map(DataBase.error_to_sql, args))})"

    def __create_query_execute(self, cursor, prefix: str, func_name: str, data: dict):
        if self.is_named_parameters:
            proc_param = ', '.join(
                [
                    f'{self.param_prefix + key} => {self.error_to_sql(value)}'
                    for key, value in data.items()
                ]
            )
            args = []
        else:
            proc_param = ",".join(str('%s') for _ in data)
            args = list(data.values())
        try:
            return cursor.execute(f"{prefix} {func_name}({proc_param})", args)
        except Exception as e:
            raise DatabaseError(
                f"""Ошибка с параметрами в {prefix} {func_name}({proc_param})
                \n {e}""")

    def function(self, attrs: dict, func_name: str, response_limit: int = -1, aggregate='*'):
        return self.__query(
            lambda cursor: self.__create_query_execute(cursor, f'SELECT {aggregate} FROM ', func_name, data=attrs),
            response_limit)

    def procedure(self, attrs: dict, func_name: str):
        def call_procedure(cursor):
            self.__create_query_execute(cursor, 'call ', func_name, data=attrs)
            try:
                self.conn.commit()
            except Exception:
                pass

        return self.__query(call_procedure, response_limit=1)


class DataBase(AbstractDataBase):
    param_prefix = 'p_'

    def __init__(self,
                 db_name: str,
                 user: str, password: str,
                 host: str = 'localhost', port: int = 5432):
        """
        Управление базой данных
        :param db_name: Название бд
        :param user: Имя пользователя
        :param password: Пароль пользователя
        :param host: Хост
        :param port: Порт
        """
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self):
        assert all([self.db_name, self.user, self.password, self.host,
                    self.port]), 'Указаны не все данные для подключения к бд'
        try:
            self.conn = psycopg2.connect(dbname=self.db_name, user=self.user,
                                         password=self.password, host=self.host, port=self.port)
        except Exception as e:
            print("Ошибка при подключении к БД", '\n', e)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
