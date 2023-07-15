from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Plots(models.Model):
    plot_name = models.CharField(max_length=255, null=False)
    plot_geometry = models.PolygonField(null=False)
    plot_owner = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
