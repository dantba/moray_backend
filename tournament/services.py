from .models import Tournament, Competitor, Participation, Match
from .forms import TournamentCreateForm, CompetitorCreateForm
from django.db.models import Prefetch
from itertools import zip_longest
from random import shuffle
from .utils import closest_power_of_two
from .exceptions import (
    TournamentFinishedError,
    TournamentNotFinishedError,
    WinnerNotInMatchError,
)
import math


def create_tournament_svc(tournament_data: TournamentCreateForm) -> Tournament:
    tournament = Tournament.objects.create(
        name=tournament_data.name,
        current_round=0,
        total_rounds=0,
    )
    return tournament


def create_competitor_svc(competitor_data: CompetitorCreateForm) -> Competitor:
    competitor = Competitor.objects.create(name=competitor_data.name)
    return competitor


def register_competitors_for_tournament_svc(
    tournament_id: int, competitor_ids: list
):
    tournament = Tournament.objects.get(pk=tournament_id)
    competitors = Competitor.objects.filter(pk__in=competitor_ids)

    participations_to_create = [
        Participation(tournament=tournament, competitor=competitor)
        for competitor in competitors
    ]
    Participation.objects.bulk_create(participations_to_create)
    num_competitors = len(competitor_ids)
    total_rounds = math.ceil(math.log2(num_competitors))
    tournament.total_rounds = total_rounds
    tournament.save()

    return "Competitors registered for tournament successfully"


def create_first_round_matches_svc(tournament_id: int):
    tournament = Tournament.objects.get(pk=tournament_id)
    competitors = list(tournament.competitors.all())

    shuffle(competitors)

    side_a_competitors = competitors[: len(competitors) // 2]
    side_b_competitors = competitors[len(competitors) // 2 :]

    teams_to_be_added = closest_power_of_two(len(competitors)) - len(
        competitors
    )

    while teams_to_be_added > 0:
        side_a_competitors.append(None)
        teams_to_be_added -= 1
        if teams_to_be_added == 0:
            break
        side_b_competitors.append(None)
        teams_to_be_added -= 1

    pairs_side_a = zip(
        side_a_competitors[: len(side_a_competitors) // 2],
        side_a_competitors[len(side_a_competitors) // 2 :],
    )
    pairs_side_b = zip(
        side_b_competitors[: len(side_b_competitors) // 2],
        side_b_competitors[len(side_b_competitors) // 2 :],
    )

    matches_to_create_a = [
        Match(
            tournament=tournament,
            competitor_1=pair[0],
            competitor_2=pair[1],
            round=1,
            side="A",
        )
        for pair in pairs_side_a
    ]
    matches_to_create_b = [
        Match(
            tournament=tournament,
            competitor_1=pair[0],
            competitor_2=pair[1],
            round=1,
            side="B",
        )
        for pair in pairs_side_b
    ]
    Match.objects.bulk_create(matches_to_create_a + matches_to_create_b)
    tournament.current_round = 1
    tournament.save()
    return "First round matches created successfully"


def create_next_round_matches_svc(tournament_id: int):
    tournament = Tournament.objects.get(pk=tournament_id)
    current_round = tournament.current_round

    if tournament.is_finished:
        raise TournamentFinishedError

    winners_side_a = Match.objects.filter(
        tournament=tournament,
        round=current_round,
        winner__isnull=False,
        side="A",
    )
    winners_side_b = Match.objects.filter(
        tournament=tournament,
        round=current_round,
        winner__isnull=False,
        side="B",
    )

    if len(winners_side_a) == 1 and len(winners_side_b) == 1:
        _create_finals(
            winners_side_a[0], winners_side_b[0], tournament, current_round
        )
        tournament.current_round += 1
        tournament.save()
        return f"Matches for final round created successfully"

    pairs_side_a = zip_longest(winners_side_a[::2], winners_side_a[1::2])
    pairs_side_b = zip_longest(winners_side_b[::2], winners_side_b[1::2])

    matches_to_create_a = [
        Match(
            tournament=tournament,
            competitor_1=pair[0].winner,
            competitor_2=pair[1].winner,
            round=current_round + 1,
            side="A",
        )
        for pair in pairs_side_a
    ]
    matches_to_create_b = [
        Match(
            tournament=tournament,
            competitor_1=pair[0].winner,
            competitor_2=pair[1].winner,
            round=current_round + 1,
            side="B",
        )
        for pair in pairs_side_b
    ]
    Match.objects.bulk_create(matches_to_create_a + matches_to_create_b)
    tournament.current_round += 1
    tournament.save()
    return f"Matches for round {current_round + 1} created successfully"


def create_match_result_svc(match_id, winner_id):
    match = Match.objects.get(id=match_id)
    if not winner_id in [match.competitor_1_id, match.competitor_2_id]:
        raise WinnerNotInMatchError
    match.winner_id = winner_id
    match.save()
    return f"{winner_id} is the winner"


def get_top_four_svc(tournament_id):
    tournaments = Tournament.objects.filter(id=tournament_id).prefetch_related(
        Prefetch(
            "match_set",
            queryset=Match.objects.filter(side__in=["F", "T"]).select_related(
                "winner", "competitor_1", "competitor_2"
            ),
        )
    )
    tournament = tournaments[0]
    if not tournament.is_finished:
        raise TournamentNotFinishedError
    result = {}
    for match in tournament.match_set.all():
        if match.side == "F":
            result["first"] = match.winner.name
            result["second"] = match.loser.name
        else:
            result["third"] = match.winner.name
            result["fourth"] = match.loser.name

    return result


def get_matches_svc(tournament_id):
    tournaments = Tournament.objects.filter(id=tournament_id).prefetch_related(
        Prefetch(
            "match_set",
            queryset=Match.objects.all()
            .select_related("winner", "competitor_1", "competitor_2")
            .order_by("id"),
        )
    )
    tournament = tournaments[0]

    result = []
    for match in tournament.match_set.all():
        match_json = {
            "id": match.id,
            "competitor_1_id": match.competitor_1_id,
            "competitor_2_id": match.competitor_2_id,
            "winner_id": match.winner_id,
            "round": match.round,
            "side": match.side,
        }
        if match.winner:
            match_json["winner"] = match.winner.name
        if match.competitor_1:
            match_json["competitor_1"] = match.competitor_1.name
        if match.competitor_2:
            match_json["competitor_2"] = match.competitor_2.name
        result.append(match_json)

    return result


def _create_finals(match_a, match_b, tournament, current_round):
    Match.objects.create(
        tournament=tournament,
        competitor_1=match_a.winner,
        competitor_2=match_b.winner,
        round=current_round + 1,
        side="F",
    )
    Match.objects.create(
        tournament=tournament,
        competitor_1=match_a.loser,
        competitor_2=match_b.loser,
        round=current_round + 1,
        side="T",
    )
