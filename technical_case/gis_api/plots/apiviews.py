from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from .models import Plots
from .serializers import (
    CreatePlotsSerializer,
    AreaSerializer,
    UpdateDeletePlotsSerializer,
)


class PlotCreate(APIView):
    """
    /plots/
    Endpoint for plots creation, specifying :
    plot_name , plot_geometry, plot_owner

    Polygon input Format : POLYGON ((-98.503358 29.335668, -98.503086 29.335668, -98.503086 29.335423, -98.50335800000001 29.335423, -98.503358 29.335668))')

    """

    serializer_class = CreatePlotsSerializer

    def post(self, request):
        plot_name = request.data["plot_name"]
        plot_geometry = request.data["plot_geometry"]
        plot_owner = request.data["plot_owner"]

        try:
            serializer = CreatePlotsSerializer(
                data={
                    "plot_name": plot_name,
                    "plot_geometry": plot_geometry,
                    "plot_owner": plot_owner,
                }
            )

            if serializer.is_valid():
                plot = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValueError:
            return Response(
                data="Bad GEOSGeometry Input", status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data="GeosGeometry Error", status=status.HTTP_400_BAD_REQUEST
            )


class PlotsListByUser(generics.ListAPIView):
    """
    /plots/<username>/

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
    Authentication is required so password must be provided in the request

    """

    serializer_class = UpdateDeletePlotsSerializer
    lookup_field = "id"

    http_method_names = ["patch", "delete"]

    def get_queryset(self):
        username = self.kwargs["username"]
        id = self.kwargs["id"]
        password = self.request.data["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return Plots.objects.filter(plot_owner=username, id=id)
