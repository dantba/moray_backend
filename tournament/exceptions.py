class TournamentFinishedError(Exception):
    message = "Tournament is finished"
    status_code = 400


class WinnerNotInMatchError(Exception):
    message = "The winner is not in this match"
    status_code = 400


class TournamentNotFinishedError(Exception):
    message = "The tournament is not finished"
