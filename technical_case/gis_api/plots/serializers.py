from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import generics, status

from django.contrib.gis.geos import GEOSGeometry

from .models import Plots


class CreatePlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plots
        fields = ["plot_name", "plot_geometry", "plot_owner"]

    def create(self, validated_data):
        try:
            validated_data["plot_geometry"] = GEOSGeometry(
                "POLYGON (" + validated_data["plot_geometry"] + ")"
            )
            return Plots.objects.create(**validated_data)

        except Exception as e:
            raise serializers.ValidationError(
                {"detail": "Bad Request"},
                code=400,
            )


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

    # def update(self, instance, validated_data):
    #     instance.plot_geometry = GEOSGeometry(
    #         "POLYGON (" + validated_data["plot_geometry"] + ")"
    #     )
    #     return super().update(instance, validated_data)

    # def update(self, instance, validated_data):
    #     raise_errors_on_nested_writes("update", self, validated_data)
    #     info = model_meta.get_field_info(instance)

    #     # Simply set each attribute on the instance, and then save it.
    #     # Note that unlike `.create()` we don't need to treat many-to-many
    #     # relationships as being a special case. During updates we already
    #     # have an instance pk for the relationships to be associated with.
    #     m2m_fields = []
    #     for attr, value in validated_data.items():
    #         if attr in info.relations and info.relations[attr].to_many:
    #             m2m_fields.append((attr, value))
    #         else:
    #             setattr(instance, attr, value)

    #     instance.save()

    #     # Note that many-to-many fields are set after updating instance.
    #     # Setting m2m fields triggers signals which could potentially change
    #     # updated instance and we do not want it to collide with .update()
    #     for attr, value in m2m_fields:
    #         field = getattr(instance, attr)
    #         field.set(value)

    #     return instance

    # def create(self, validated_data):
    #     try:
    #         validated_data["plot_geometry"] = GEOSGeometry(
    #             "POLYGON (" + validated_data["plot_geometry"] + ")"
    #         )
    #         return Plots.objects.create(**validated_data)

    #     except Exception as e:
    #         raise serializers.ValidationError(
    #             {"detail": "Bad Request"},
    #             code=400,
    #         )
