from django.urls import path
from django.views.generic import TemplateView
from tournament import views

app_name = "tournament"

urlpatterns = [
    path("competitor/", views.create_competitor, name="create_competitor"),
    path("tournament/", views.create_tournament, name="create_tournament"),
    path(
        "tournament/<int:tournament_id>/competitor/",
        views.register_competitors_for_tournament_view,
        name="register_competitors_for_tournament",
    ),
    path(
        "tournament/<int:tournament_id>/create-first-round-matches/",
        views.create_first_round_matches,
        name="create_first_round_matches",
    ),
    path(
        "tournament/<int:tournament_id>/create-next-round-matches/",
        views.create_next_round_matches,
        name="create_next_round_matches",
    ),
    path(
        "tournament/<int:tournament_id>/match/<int:match_id>/",
        views.create_match_result,
        name="create_match_result",
    ),
    path(
        "tournament/<tournament_id>/result",
        views.get_top_four,
        name="get_top_four",
    ),
    path(
        "tournament/<tournament_id>/match",
        views.get_tournament_matches,
        name="get_tournament_matches",
    ),
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
]
