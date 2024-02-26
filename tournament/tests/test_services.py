import pytest
from model_bakery import baker
from tournament.models import Tournament, Competitor, Match
from tournament.forms import TournamentCreateForm, CompetitorCreateForm
from tournament.services import (
    create_tournament_svc,
    create_competitor_svc,
    register_competitors_for_tournament_svc,
    create_first_round_matches_svc,
    create_next_round_matches_svc,
)


@pytest.fixture
def competitors():
    return baker.make("tournament.Competitor", _quantity=6)


@pytest.fixture
def tournament():
    return baker.make("tournament.Tournament")


@pytest.fixture
def match():
    return baker.make("tournament.Match")


@pytest.mark.django_db
def test_create_tournament_svc():
    form_data = {"name": "Test Tournament"}
    form = TournamentCreateForm.parse_obj(form_data)
    create_tournament_svc(form)
    assert Tournament.objects.filter(name="Test Tournament").exists()


@pytest.mark.django_db
def test_create_competitor_svc():
    form_data = {"name": "Test Competitor"}
    form = CompetitorCreateForm.parse_obj(form_data)
    create_competitor_svc(form)
    assert Competitor.objects.filter(name="Test Competitor").exists()


@pytest.mark.django_db
def test_register_competitors_for_tournament_svc(tournament, competitors):
    competitor_ids = [competitor.id for competitor in competitors]
    message = register_competitors_for_tournament_svc(
        tournament.id, competitor_ids
    )
    assert message == "Competitors registered for tournament successfully"
    assert tournament.competitors.count() == 6


@pytest.mark.django_db
def test_create_first_round_matches_svc(tournament, competitors):

    tournament.competitors.set(competitors)

    create_first_round_matches_svc(tournament.id)

    matches = Match.objects.filter(tournament=tournament, round=1)
    assert matches.exists()

    expected_matches_count = 4
    assert matches.count() == expected_matches_count

    tournament.refresh_from_db()
    assert tournament.current_round == 1


@pytest.mark.django_db
def test_create_next_round_matches_svc(tournament):

    current_round = 1
    tournament.current_round = current_round
    tournament.save()
    matches = []
    for i in range(4):
        match = baker.make(
            "tournament.Match",
            tournament=tournament,
            round=current_round,
            side="A",
            winner=baker.make("tournament.Competitor"),
        )
        matches.append(match)
    for i in range(4):
        match = baker.make(
            "tournament.Match",
            tournament=tournament,
            round=current_round,
            side="B",
            winner=baker.make("tournament.Competitor"),
        )
        matches.append(match)

    create_next_round_matches_svc(tournament.id)

    next_round_matches = Match.objects.filter(
        tournament=tournament, round=current_round + 1
    )
    assert next_round_matches.exists()

    expected_matches_count = 4
    assert next_round_matches.count() == expected_matches_count
    tournament.refresh_from_db()
    assert tournament.current_round == current_round + 1
