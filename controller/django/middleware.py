from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from psycopg2 import DatabaseError
from pydantic import ValidationError


class ErrorMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            return JsonResponse({'errors': exception.errors()}, status=500)
        elif isinstance(exception, DatabaseError):
            return JsonResponse({'message': str(exception), 'type': 'db'}, status=500)
        else:
            raise exception
