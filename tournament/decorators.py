from functools import wraps
from django.http import JsonResponse
from django.conf import settings


def require_post(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed"}, status=405)
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_get(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.method != "GET":
            return JsonResponse({"error": "Method not allowed"}, status=405)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
