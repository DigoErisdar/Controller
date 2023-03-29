from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from pydantic import ValidationError


class ErrorMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            return JsonResponse({'errors': exception.errors()}, status=500)
        else:
            raise exception
