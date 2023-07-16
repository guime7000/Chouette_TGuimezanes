from rest_framework import serializers

from .models import Plots


class CreatePlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plots
        fields = ["plot_name", "plot_geometry", "plot_owner"]


class AreaSerializer(serializers.ModelSerializer):
    plot_geometry = serializers.SerializerMethodField(method_name="get_plot_geometry")
    plot_area = serializers.SerializerMethodField(method_name="get_plot_area")

    class Meta:
        model = Plots
        fields = ["id", "plot_name", "plot_geometry", "plot_area"]

    def get_plot_geometry(self, obj: Plots):
        return obj.plot_geometry.coords

    def get_plot_area(self, obj: Plots):
        return obj.plot_geometry.area


class UpdateDeletePlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plots
        fields = ["id", "plot_name", "plot_geometry", "plot_owner"]
