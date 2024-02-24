from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tournament
from .serializers import TournamentSerializer


@csrf_exempt
def tournament_create(request):
    if request.method == "POST":
        serializer = TournamentSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
