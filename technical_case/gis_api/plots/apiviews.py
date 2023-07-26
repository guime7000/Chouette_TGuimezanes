from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from .models import Plots
from .serializers import (
    CreatePlotsSerializer,
    AreaSerializer,
    UpdateDeletePlotsSerializer,
)


class PlotCreate(generics.CreateAPIView):
    """
    /plots/
    Endpoint for plot creation, specifying :
    plot_name, plot_geometry, plot_owner

    Polygon input Format : (-98.503358 29.335668, -98.503086 29.335668, -98.503086 29.335423, -98.50335800000001 29.335423, -98.503358 29.335668)

    """

    serializer_class = CreatePlotsSerializer


class PlotsListByUser(generics.ListAPIView):
    """
    /plots/<username>

    Endpoint to list all plots owned by user <username>
    """

    serializer_class = AreaSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.order_by("id")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        username = self.kwargs["username"]
        get_object_or_404(User, username=username)
        return Plots.objects.filter(plot_owner=username)


class PlotUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    """
    /plots/<username>/<id>

    Endpoint to update (PATCH method) or DELETE a plot
    Authentication is required so <username>'s password must be provided in the request

    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    serializer_class = UpdateDeletePlotsSerializer
    lookup_field = "id"

    http_method_names = ["patch", "delete"]

    def get_queryset(self):
        username = self.kwargs["username"]
        id = self.kwargs["id"]

        if self.request.user.is_authenticated:
            return Plots.objects.filter(plot_owner=username, id=id)
