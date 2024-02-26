from django.shortcuts import render

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Tournament, Competitor, Match
from .forms import (
    CompetitorCreateForm,
    TournamentCreateForm,
    CompetitorListForm,
    MatchResultRequest,
)
from .services import (
    create_competitor_svc,
    create_tournament_svc,
    create_next_round_matches_svc,
    create_first_round_matches_svc,
    register_competitors_for_tournament_svc,
    create_match_result_svc,
    get_top_four_svc,
    get_matches_svc,
)
from .decorators import require_post, require_get
from .exceptions import TournamentFinishedError, WinnerNotInMatchError
import json
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator


@csrf_exempt
@require_post
def create_tournament(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        tournament_form = TournamentCreateForm(**data)
        tournament = create_tournament_svc(tournament_form)

        return JsonResponse(
            {
                "id": tournament.id,
                "name": tournament.name,
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_post
def create_competitor(request: HttpRequest) -> JsonResponse:
    try:
        competitor_form = CompetitorCreateForm.parse_raw(request.body)
        competitor = create_competitor_svc(competitor_form)

        return JsonResponse(
            {"id": competitor.id, "name": competitor.name}, status=201
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_post
def register_competitors_for_tournament_view(
    request: HttpRequest, tournament_id: int
) -> JsonResponse:
    try:
        form = CompetitorListForm.parse_raw(request.body)
        message = register_competitors_for_tournament_svc(
            tournament_id, form.competitor_ids
        )
        return JsonResponse({"message": message}, status=200)
    except Tournament.DoesNotExist:
        return JsonResponse({"error": "Tournament not found"}, status=404)
    except Competitor.DoesNotExist:
        return JsonResponse(
            {"error": "One or more competitors not found"}, status=404
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_post
def create_first_round_matches(
    request: HttpRequest, tournament_id: int
) -> JsonResponse:
    try:
        message = create_first_round_matches_svc(tournament_id=tournament_id)
        return JsonResponse({"message": message}, status=200)
    except Tournament.DoesNotExist:
        return JsonResponse({"error": "Tournament not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_post
def create_next_round_matches(
    request: HttpRequest, tournament_id: int
) -> JsonResponse:
    try:
        message = create_next_round_matches_svc(tournament_id=tournament_id)
        return JsonResponse({"message": message}, status=200)
    except TournamentFinishedError as e:
        return JsonResponse({"error": e.message}, status=e.status_code)
    except Tournament.DoesNotExist:
        return JsonResponse({"error": "Tournament not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_post
def create_match_result(
    request: HttpRequest, tournament_id: int, match_id: int
) -> JsonResponse:
    try:
        form = MatchResultRequest.parse_raw(request.body)
        message = create_match_result_svc(
            match_id=match_id, winner_id=form.winner_id
        )
        return JsonResponse({"message": message}, status=200)
    except Match.DoesNotExist:
        return JsonResponse({"error": "Match not found"}, status=404)
    except WinnerNotInMatchError as e:
        return JsonResponse({"error": e.message}, status=e.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_get
def get_top_four(request: HttpRequest, tournament_id: int) -> JsonResponse:
    try:
        result = get_top_four_svc(tournament_id=tournament_id)
        return JsonResponse({"result": result}, status=200)
    except Tournament.DoesNotExist:
        return JsonResponse({"error": "Tournament not found"}, status=404)


def get_tournament_matches(
    request: HttpRequest, tournament_id: int
) -> JsonResponse:
    try:
        result = get_matches_svc(tournament_id=tournament_id)
        return JsonResponse({"result": result}, status=200)
    except Tournament.DoesNotExist:
        return JsonResponse({"error": "Tournament not found"}, status=404)
