from django.urls import path, re_path

from .apiviews import (
    PlotCreate,
    PlotsListByUser,
    PlotUpdateDelete,
)

urlpatterns = [
    path("plots/", PlotCreate.as_view(), name="plot_create"),
    re_path(
        "^plots/(?P<username>.+)/(?P<id>.+)",
        PlotUpdateDelete.as_view(),
        name="plots_updateDelete",
    ),
    re_path(
        "^plots/(?P<username>.+)",
        PlotsListByUser.as_view(),
        name="plots_list",
    ),
]
