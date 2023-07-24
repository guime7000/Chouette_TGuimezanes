# Technical Case - Thomas Guimezanes

This project gives you the configuration and API's Documentation for the technical case.

## How to deploy :

### Start the API

To start the django api, you have a docker-compose file. 
1. Build the containers
```bash
docker compose build
```
2. launch the project
```bash
docker compose up -d
```

### Run the migrations

Once the API is up and running, you can start developing on it.
First you will need to run the first django migrations.
1. Open a console on the container that is running the API.
```bash
docker compose exec api /bin/bash
```
2. Run the migrations
```bash
python manage.py migrate
```
### Create a suseruser for Django's USER Table administration:

In a console on the container that is running the API:

```bash
python3 manage createsuperuser
```
and fill the required fields.

### Create the users who'll need to use this API

As some endpoints of this API require an authentication, you'll need to create users in Django's User database to be able to manipulate plots.

You can create these users via the admin panel [http://localhost:8000/admin](http://localhost:8000/admin) or via [create_user function]( https://docs.djangoproject.com/en/4.2/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user)


## API Documentation:

This API is aimed for (agricultural) plot manipulation.

Using the 3 URLs below, you'll be able to :

- **create** a plot via ``http://localhost:8000/plots/``
- **list** all plots owned by a specific user via ``http://localhost:8000/plots/<username>``
- **update** or **delete** a plot via ``http://localhost:8000/plots/<username>/<id>``

Update and Delete operations need Authentication. This is done using [https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication] (DRF TokenAuthentication).

Provide a {username, password} payload to /token_delivery/ endpoints and you'll get an authentication Token in return response.

### &rarr; Create a plot:
```
- Endpoint: /plots/
- Http method allowed: POST
- data required: 

       - plot_name (not NULL)
       - plot_geometry (GEOSGEOMETRY Polygon only with SRID=4326)
       - plot_owner (not NULL)

- Http Return code : 201 Created
```

A plot is considered as the association of a ***plot name***, with a ***GEOSGeometry Polygon type*** geometry and ***a plot owner***.

```
***Note: A plot name is NOT considered as unique in the postGIS Table. It is thus possible for a user to create different plots geometries with the same name.***
```

For example:

To create a new plot in database, you'll need to provide three key/values pairs. 
- "plot_name": "ABCDE"
- "plot_geometry": (1 1, 0 50, 50 50, 50 0, 1 1)"
- "plot_owner": "user1"

Type:

```bash
curl -iX POST 
-H "Content-Type: application/json" 
-d '{"plot_name": "ABCDE", "plot_geometry":"(1 1, 0 50, 50 50, 50 0, 1 1)", "plot_owner":"user1"}' 
http://localhost:8000/plots/
```
- which will create a plot named **ABCDE** with a **GEODjango Polygon** type object of coords **(1 1, 0 50, 50 50, 50 0, 1 1)** owned by **user1**
- and return the JSON object 
    ```json
    {"plot_name":"ABCDE","plot_geometry":"SRID=4326;POLYGON ((1 1, 0 50, 50 50, 50 0, 1 1))","plot_owner":"user1"}
    ```
    with return status code 201_Created.

Empty fields, bad user name or wrong GEOSGeometry Polygon input will return a **400_bad_request** http status code.


### &rarr; List plots:
```
- Endpoint: /plots/<username>
- Http method allowed: GET
- data required: None
- Http Return code : 200 OK
```
You can list all plots owned by a specific user. 

Reaching ``/plots/<username>`` will return a list of all plots owned by ``<username>``with, for each plot :

    - the unique **id** of the plot (useful and used to update or delete plot as plots names can be duplicated in db)
    - the coordinates of the plot's geometry
    - the area of the plot's geometry

As a suite of the previously plot creation example, typing:

```bash
curl -iX GET 
http://localhost:8000/plots/user1
```

will return all owner's plots properties:

```json
[{"id":1,"plot_name":"ABCDE","plot_geometry":[[[1.0,1.0],[0.0,50.0],[50.0,50.0],[50.0,0.0],[1.0,1.0]]],"plot_area":2450.0},]
```
with return status_code 200_OK.

Trying to list plots of an unknown user will lead to a **404_Not_found** http status code.


### &rarr; Update a plot:
```
- Endpoint: /plots/<username>/<id>
- Http method allowed: PATCH
- data required: 
        - "plot_name" AND / OR "plot_geometry"
- header shall contain "Authorization: Token <userToken>"
    
- Http Return code : 200 OK
```

To be allowed to update a plot, its owner must be authenticated using his password.

If authentication fails, API will return a 404_error_code

* To update a plot name, specify the new name of the plot in a "plot_name" field and send it with the password:

```bash
curl -iX PATCH 
-H "Content-Type: application/json" 
-H "Authorization: Token <YOUR_USER_TOKEN>"
-d '{"plot_name":"plot27"}' 
http://localhost:8000/plots/user1/1
```
returns 

```json
{"id":1,"plot_name":"plot27","plot_geometry":"SRID=4326;POLYGON ((1 1, 0 50, 50 50, 50 0, 1 1))","plot_owner":"user1"}
```

and http status_code 200_OK

* To update a plot geometry, specify the new geometry using the POLYGON ( [...]) GEOSGeometry syntax:

```bash
curl -iX PATCH 
-H "Content-Type: application/json" 
-H "Authorization: Token <YOUR_USER_TOKEN>"
-d '{"plot_geometry":"POLYGON ((1 1, 0 100, 100 100, 100 0, 1 1))"}' 
http://localhost:8000/plots/update/user1/1
```

returns :

```json
{"id":1,"plot_name":"plot27","plot_geometry":"SRID=4326;POLYGON ((1 1, 0 100,100 100, 100 0, 1 1))","plot_owner":"user1"}
```

and http status_code 200_OK


* To update plot name **AND** plot geometry: Combine both `plot_name` and `plot_geometry` fields in the request sent to API !

* To change plot owner :

Once authenticated, a plot owner is given the possibility to change the owner of the plot. But this owner is then loosing all rights for updating and deleting this plot property:

```bash
curl -iX PATCH 
-H "Content-Type: application/json"
-H "Authorization: Token <YOUR_USER_TOKEN>"
-d '{"plot_owner":"user2"}' 
http://localhost:8000/plots/update/user1/2
```
will update ``plot_owner``fields attribute from ``user1`` to ``user2``

### &rarr; Delete a plot :
```
- Endpoint: /plots/<username>/<id>
- Http method allowed: DELETE
- data required: password
- header shall contain "Authorization: Token <userToken>"
    
- Http Return code : 204 No_Content
```
As for updating a plot, the owner of a plot has to be authenticated.

Assuming **user2** :

- exists in djangos User base
- is the owner of the plot whith id = 2
- has given the correct password in his request

Then typing :

```bash
curl -iX DELETE 
-H "Content-Type: application/json" 
-H "Authorization: Token <YOUR_USER_TOKEN>"
http://localhost:8000/plots/user2/2
```

will return status code 204_No_content as requested plot has been deleted.

If one tries to access a non-existent plot, he'll receive a **404 Not Found** error code in response.
