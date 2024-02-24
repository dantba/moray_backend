from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(auto_now_add=True)
    competitors = models.ManyToManyField("Competitor", through="Participation")


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
        Competitor, related_name="competitor_1", on_delete=models.CASCADE
    )
    competitor_2 = models.ForeignKey(
        Competitor, related_name="competitor_2", on_delete=models.CASCADE
    )
    winner = models.ForeignKey(
        Competitor, related_name="winner", on_delete=models.CASCADE, null=True
    )
    round = models.IntegerField()


class Result(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    result = models.CharField(
        max_length=1
    )  # '1' for competitor_1, '2' for competitor_2
