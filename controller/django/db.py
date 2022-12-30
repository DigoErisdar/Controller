from django.db import connections

from controller.core.db import DataBase


class DjangoDataBase(DataBase):

    def __init__(self, db_name: str = 'default', *args):
        super(DjangoDataBase, self).__init__(*args)
        self.db_name = db_name

    def __enter__(self):
        self.conn = connections[self.db_name]
        return self
