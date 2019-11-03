# DjangoReactUserAuth-backend

## Project Purpose
---------------------
* Allow user to signup with credentials like username, password, firstname and lastname using Python REST API
which can be accessed from `http:\\localhost:8000\user_auth\signup` after running the server
* After signup it is stored in the sqlite database
* After this user can signin using username and password via API `http:\\localhost:8000\login`
* If SignIn is successfull a `token` will be generated otherwise gives `error`
* This `token` is currently valid for 1 hour(can be changed later)
* we can use the `token` with the GET API call on `http:\\localhost:8000\user_auth\currentuser` to get the current logged in user
* this is only the backend which will be used with a React Frontend where the API are already integrated.

This is a backend part use it with frontend
[ReactFrontend](https://github.com/harshdeepkanhai/DjangoReactUserAuth-frontend)


-----------------------------------------
* Install python3 and pip
* clone this directory
* cd into DjangoReactUserAuth-backend
* run `pip install -r requirements.txt `
* run `python manage.py migrate`
* run `python manage.py runserver`
* The server will now be started on `http:\\localhost:8000`
