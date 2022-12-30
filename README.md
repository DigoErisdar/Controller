# Контроллер для работы с хранимыми процедурами

## Пример использования с фунциями

```python
from controller.core.models import FunctionModel
from typing import Optional


class GetOrder(FunctionModel):
    """Хранимка для получения списка заказов"""
    _func_name = 'data.get_order'
    id: Optional[int]
    status_id: Optional[int]
    cemetery_id: Optional[int]
    customer_id: Optional[int]
    search: str = ''
    rows: Optional[int] = None
    page: int = 1
    user_id: Optional[int]


order = GetOrder(id=1984).get()  # Вернет 1 объект {}
all_orders = GetOrder(id=1984).all()  # Вернет все товары [{}]
top_5_orders = GetOrder(status_id=2).get(5)  # Вернет 5 заказов
all_orders_count = GetOrder().length()  # Вернет кол-во заказов 1923
   ```

## Пример использования с процедурами

```python
from controller.core.models import ProcedureModel
from typing import Optional


class RemoveOrder(ProcedureModel):
    """Хранимка для удаление заказа"""
    _func_name = 'data.remove_order'
    id: Optional[int]
    status_id: Optional[int]
    cemetery_id: Optional[int]
    customer_id: Optional[int]
    user_id: Optional[int]


response = RemoveOrder(id=1984).execute()  # Удалит заказ
```

## Поддержка Django

Основная часть расширения включает в себя особенность в качестве параметра в хранимку передавать request,
а также специальное поле для получения user_id (AuthUser)

```python
from controller.core.models import FunctionModel
from controller.django.models import DjangoModelMixin
from controller.django.fields import AuthUser
from django.http.response import JsonResponse
from typing import Optional
from controller.core.fields import Const


class GetOrder(FunctionModel, DjangoModelMixin):
    """Комментарий"""
    _func_name = 'data.get_order'
    id: Optional[int]
    status_id: Optional[int]
    cemetery_id: Optional[int]
    customer_id: Optional[int]
    search: str = ''
    rows: Optional[int] = None
    page: int = 1
    user_id: AuthUser


class GetOrderCompleted(GetOrder):
    status_id: Const = 2


def home(request):
    return JsonResponse({'item': GetOrderCompleted(request).get()})
# Хранимка get_order заберет в себя все необходимые параметры,
# и провалидирует их и перезапишет status_id на 2. То есть с фронта можно не отправлять пустые значения или значения,
# которые не требуют переопределения

```

## Валидация ошибок и создание своих полей

Есть возможность прописать свое поле для каких-то данных, например, для телефона у нас должны быть числа и длинной
равной 10

```python
from controller.core.models import FunctionModel
from controller.core.fields import CustomField
from pydantic import ValidationError


class Phone(CustomField):
    __root__ = str

    @classmethod
    def validate(cls, value, values, config, field) -> str:
        value = str(value)
        if value and (not value.isdigit() or len(value) != 10):
            raise ValueError("Это не номер телефона")
        return value


class GetOrder(FunctionModel):
    """Комментарий"""
    _func_name = 'data.get_order'
    phone: Phone = ''


try:
    GetOrder(phone=12)
except ValidationError as e:
    print(e.json())
"""
[
  {
    "loc": [
      "phone"
    ],
    "msg": "Это не номер телефона",
    "type": "value_error"
  }
]
"""
```

Если данное поле валидацию не пройдет, то мы получим ошибку, которую можно вернуть в формате json

# FastAPI

Использование данного подхода с FastAPI раскрывается еще сильнее,
мы получаем грубо говоря автодокументирование нашего api с которого еще и выполнить запрос можно

```python
from controller.core.models import FunctionModel
from controller.core.db import DataBase
from typing import Optional
from fastapi import FastAPI, Depends

app = FastAPI()
db = DataBase()


class GetOrder(FunctionModel):
    """Хранимка для получения заказов"""
    _func_name = 'data.get_order'
    _db = db
    id: Optional[int]
    status_id: Optional[int]


@app.get('/')
def home(data: GetOrder = Depends()):
    return data
```

Результат:
![](https://i.ibb.co/QYDv8q2/photo-2022-12-29-15-15-29.jpg)