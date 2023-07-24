from django.urls import path, re_path

from rest_framework.authtoken import views

from .apiviews import (
    PlotCreate,
    PlotsListByUser,
    PlotUpdateDelete,
)

urlpatterns = [
    path("token_delivery/", views.obtain_auth_token, name="token_delivery"),
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
