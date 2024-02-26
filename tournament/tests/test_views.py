import json
import pytest
from django.test import RequestFactory
from tournament.models import Match
from model_bakery import baker
from tournament.views import (
    create_tournament,
    create_competitor,
    register_competitors_for_tournament_view,
    create_first_round_matches,
    create_next_round_matches,
    create_match_result,
    get_top_four,
    get_tournament_matches,
)


def switch_char(char):
    if char == "A":
        return "B"
    else:
        return "A"


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def competitors():
    return baker.make("tournament.Competitor", _quantity=8)


@pytest.fixture
def tournament(competitors):
    tournament = baker.make("tournament.Tournament", name="Tournament")
    for competitor in competitors:
        tournament.competitors.add(competitor)
    return tournament


@pytest.fixture
def competitors_without_tournament():
    return baker.make("tournament.Competitor", _quantity=8)


@pytest.fixture
def tournament_without_competitors(competitors):
    return baker.make("tournament.Tournament", name="Tournament")


@pytest.fixture
def matches(tournament):
    matches = []
    competitors = tournament.competitors.all()
    competitor_pairs = [
        competitors[i : i + 2] for i in range(0, len(competitors), 2)
    ]
    side = "A"
    for pair in competitor_pairs:
        match = baker.make(
            "tournament.Match",
            competitor_1=pair[0],
            competitor_2=pair[1],
            tournament=tournament,
            winner=pair[1],
            round=0,
            side=side,
        )
        side = switch_char(side)
        matches.append(match)
    return matches


@pytest.fixture()
def top_four_competitors():
    return baker.make("tournament.Competitor", _quantity=8)


@pytest.fixture()
def top_four_tournament(top_four_competitors):
    tournament = baker.make(
        "tournament.Tournament",
        name="Tournament Top 4",
        current_round=2,
        total_rounds=2,
    )
    for competitor in top_four_competitors:
        tournament.competitors.add(competitor)
    return tournament


@pytest.fixture()
def final_matches(top_four_tournament):
    competitors = top_four_tournament.competitors.all()
    competitor_pairs = [
        competitors[i : i + 2] for i in range(0, len(competitors), 2)
    ]
    final = baker.make(
        "tournament.Match",
        tournament=tournament,
        competitor_1=competitor_pairs[0],
        competitor_2=competitor_pairs[1],
        winner=competitor_pairs[1],
        side="F",
    )
    third = baker.make(
        "tournament.Match",
        tournament=tournament,
        competitor_1=competitor_pairs[2],
        competitor_2=competitor_pairs[3],
        winner=competitor_pairs[3],
        side="T",
    )
    return [final, third]


@pytest.mark.django_db
def test_create_tournament(factory):
    data = {"name": "Test Tournament"}
    request = factory.post(
        "/api/v1/tournament/", json.dumps(data), content_type="application/json"
    )
    response = create_tournament(request)
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_competitor(factory):
    data = {"name": "Test Competitor"}
    request = factory.post(
        "/api/v1/competitor/", json.dumps(data), content_type="application/json"
    )
    response = create_competitor(request)
    assert response.status_code == 201


@pytest.mark.django_db
def test_register_competitors_for_tournament(
    factory, tournament_without_competitors, competitors_without_tournament
):
    competitor_ids = [
        competitor.id for competitor in competitors_without_tournament
    ]
    data = {"competitor_ids": competitor_ids}
    request = factory.post(
        f"/api/v1/tournament/{tournament_without_competitors.id}/competitor/",
        json.dumps(data),
        content_type="application/json",
    )
    response = register_competitors_for_tournament_view(
        request, tournament_id=tournament_without_competitors.id
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_first_round_matches(factory, tournament):
    request = factory.post(
        f"/api/v1/tournament/{tournament.id}/create-first-round-matches/"
    )
    response = create_first_round_matches(request, tournament_id=tournament.id)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_next_round_matches(factory, tournament, matches):
    request = factory.post(
        f"/api/v1/tournament/{tournament.id}/create-next-round-matches/"
    )
    response = create_next_round_matches(request, tournament_id=tournament.id)
    assert response.status_code == 200


@pytest.mark.django_db
def test_set_match_result(factory, matches, tournament):
    match = matches[0]
    data = {"winner_id": match.competitor_2.id}
    request = factory.post(
        f"/api/v1/tournament/{tournament.id}/match/{match.id}/",
        json.dumps(data),
        content_type="application/json",
    )
    response = create_match_result(request, tournament.id, match.id)
    updated_match = Match.objects.get(pk=match.id)
    assert updated_match.winner == match.competitor_2
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_top_four_participants(factory, final_matches, top_four_tournament):
    request = factory.get(
        f"/api/v1/tournament/{top_four_tournament.id}/result/"
    )
    response = get_top_four(request, tournament_id=top_four_tournament.id)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_matches_for_tournament(
    factory, top_four_tournament, final_matches
):
    request = factory.get(f"/api/v1/tournament/{top_four_tournament.id}/match/")
    response = get_tournament_matches(
        request, tournament_id=top_four_tournament.id
    )
    assert response.status_code == 200
