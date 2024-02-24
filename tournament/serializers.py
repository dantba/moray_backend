from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json


class TournamentSerializer:
    def __init__(self, tournament):
        self.tournament = tournament

    def serialize(self):
        return {
            "id": self.tournament.id,
            "name": self.tournament.name,
        }


class CompetitorSerializer:
    def __init__(self, competitor):
        self.competitor = competitor

    def serialize(self):
        return {
            "id": self.competitor.id,
            "name": self.competitor.name,
        }


class MatchSerializer:
    def __init__(self, match):
        self.match = match

    def serialize(self):
        return {
            "id": self.match.id,
            "tournament_id": self.match.tournament_id,
        }


class MatchResultSerializer:
    def __init__(self, match):
        self.match = match

    def serialize(self):
        return {
            "id": self.match.id,
            "result": self.match.result,
        }
