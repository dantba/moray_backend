from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    current_round = models.IntegerField()
    total_rounds = models.IntegerField()
    competitors = models.ManyToManyField("Competitor", through="Participation")

    @property
    def is_finished(self):
        return self.current_round == self.total_rounds


class Competitor(models.Model):
    name = models.CharField(max_length=100)


class Participation(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tournament", "competitor")


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    competitor_1 = models.ForeignKey(
        Competitor,
        related_name="competitor_1",
        on_delete=models.CASCADE,
        null=True,
    )
    competitor_2 = models.ForeignKey(
        Competitor,
        related_name="competitor_2",
        on_delete=models.CASCADE,
        null=True,
    )
    winner = models.ForeignKey(
        Competitor, related_name="winner", on_delete=models.CASCADE, null=True
    )
    side = models.CharField()
    round = models.IntegerField()

    @property
    def loser(self):
        if not self.winner:
            return None
        if self.competitor_1 == self.winner:
            return self.competitor_2
        return self.competitor_1
