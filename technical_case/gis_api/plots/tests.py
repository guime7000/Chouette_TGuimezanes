from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from plots.models import Plots, User


class CreatePlotTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="user1")
        self.user.set_password("password_1234")
        self.user.save()

    def test_create_plot(self):
        """
        Ensure a plot is created with correct fields values in postGIS DB
        """
        url = "/plots/"
        data = {
            "plot_name": "plot1",
            "plot_geometry": "(0.0 0.0,  0.1 0, 0.1 0.1, 0.0 0.1, 0.0 0.0)",
            "plot_owner": "user1",
        }
        response = self.client.post(url, data=data, format="json")

        createdPlot = Plots.objects.filter(id=1)

        createdPlotName = createdPlot.values("plot_name")[0]["plot_name"]
        createdPlotGeometry = createdPlot.values("plot_geometry")[0]["plot_geometry"]
        createdPlotOwner = createdPlot.values("plot_owner")[0]["plot_owner"]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(createdPlotName, "plot1")
        self.assertEqual(
            createdPlotGeometry,
            "SRID=4326;POLYGON ((0.0 0.0,  0.1 0, 0.1 0.1, 0.0 0.1, 0.0 0.0))",
        )
        self.assertEqual(
            User.objects.filter(username=createdPlotOwner).values("username")[0][
                "username"
            ],
            "user1",
        )

    def test_create_plot_with_bad_geometry(self):
        """
        Ensure non parsable GEOSGeometry instructions are not allowed
        """
        url = "/plots/"
        data = {
            "plot_name": "plot1",
            "plot_geometry": "(0.0 0.0,(0.1 0), 0.1 0.1, 0.0 0.1, 0.0 0.0)",
            "plot_owner": "user1",
        }
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plot_with_unknown_user(self):
        """
        Ensure unknown user can't create a plot
        """
        url = "/plots/"
        data = {
            "plot_name": "plot1",
            "plot_geometry": "(0.0 0.0,  0.1 0, 0.1 0.1, 0.0 0.1, 0.0 0.0)",
            "plot_owner": "user",
        }
        response = self.client.post(url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ListPlotsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.user.set_password("password_1234")
        self.user.save()

        Plots.objects.create(
            plot_name="plot1",
            plot_geometry="POLYGON((0.0 0.0,  0.1 0.0, 0.1 0.1, 0.0 0.1, 0.0 0.0))",
            plot_owner=User.objects.filter(username="user1")[0],
        )

        Plots.objects.create(
            plot_name="plot2",
            plot_geometry="POLYGON ((0.0 0.0,  1.0 0.0, 1.0 1.0, 0.0 1.0, 0.0 0.0))",
            plot_owner=User.objects.filter(username="user1")[0],
        )

    def test_returned_plot_list_length(self):
        """
        Ensure that plot list endpoints returns ALL plots in DB for a specific user
        """
        url = "/plots/user1"

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class UpdateDeletePlotTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.user.set_password("password_1234")
        self.user.save()

        self.user = User.objects.create(username="user2")
        self.user.set_password("password_abcd")
        self.user.save()

        Plots.objects.create(
            plot_name="plot1",
            plot_geometry="POLYGON((0.0 0.0,  0.1 0.0, 0.1 0.1, 0.0 0.1, 0.0 0.0))",
            plot_owner=User.objects.filter(username="user1")[0],
        )

        Plots.objects.create(
            plot_name="plot11",
            plot_geometry="POLYGON ((0.0 0.0,  1.0 0.0, 1.0 1.0, 0.0 1.0, 0.0 0.0))",
            plot_owner=User.objects.filter(username="user1")[0],
        )

        Plots.objects.create(
            plot_name="plot2",
            plot_geometry="POLYGON((0.0 0.0,  0.1 0.0, 0.1 0.1, 0.0 0.1, 0.0 0.0))",
            plot_owner=User.objects.filter(username="user2")[0],
        )

        Plots.objects.create(
            plot_name="plot21",
            plot_geometry="POLYGON ((0.0 0.0,  1.0 0.0, 1.0 1.0, 0.0 1.0, 0.0 0.0))",
            plot_owner=User.objects.filter(username="user2")[0],
        )

    def test_update_plot_name_with_wrong_password_impossible(self):
        """
        Ensure that updating plot name with wrong password is impossible
        """
        url = "/plots/user1/1"

        self.user2Token = self.client.post(
            "/token_delivery/", data={"username": "user2", "password": "password_abcd"}
        ).data["token"]

        response = self.client.patch(
            url,
            HTTP_Authorization=f"Token {self.user2Token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_plot_name_with_authenticated_user(self):
        """
        Ensure that update plot name and plot_geometry is OK when authenticated

        plot1 becomes plot100 and plot_geometry becomes "POLYGON((0.0 0.0,  0.2 0.0, 0.2 0.2, 0.0 0.2, 0.0 0.0))"
        """

        first_plot_id = self.client.get("/plots/user1").data[0]["id"]

        url = f"/plots/user1/{first_plot_id}"

        self.user1Token = self.client.post(
            "/token_delivery/", data={"username": "user1", "password": "password_1234"}
        ).data["token"]

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1Token)

        response = self.client.patch(
            url,
            data={
                "plot_name": "plot100",
                "plot_geometry": "POLYGON((0.0 0.0,  0.2 0.0, 0.2 0.2, 0.0 0.2, 0.0 0.0))",
            },
            format="json",
        )
        updatedPlot = Plots.objects.filter(id=first_plot_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updatedPlot[0].plot_name, "plot100")
        self.assertEqual(
            updatedPlot[0].plot_geometry,
            "SRID=4326;POLYGON ((0 0, 0.2 0, 0.2 0.2, 0 0.2, 0 0))",
        )

    def test_delete_plot_with_wrong_password_impossible(self):
        """
        Ensure that deleting plot name with wrong password is impossible
        """
        url = "/plots/user2/6"

        self.user2Token = self.client.post(
            "/token_delivery/",
            data={"username": "user2", "password": "password_abcd"},
        ).data["token"]

        response = self.client.delete(
            url,
            HTTP_Authorization=f"Token {self.user2Token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_plot_empties_plot_attribute_in_db(self):
        """
        Ensure that deleting a plot when authenticated is removing it from DB
        """
        url = "/plots/user2/6"

        original_plots_count = Plots.objects.count()

        self.user1Token = self.client.post(
            "/token_delivery/", data={"username": "user1", "password": "password_1234"}
        ).data["token"]

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1Token)

        response = self.client.delete(url)

        current_plots_count = Plots.objects.count()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(current_plots_count, original_plots_count - 1)
