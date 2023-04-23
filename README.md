# Social Media API

API for a social media platform made using Django and Django REST framework.

## Features

- Documentation at api/doc/swagger/
#### Users
- JWT authentication for login
- Logout with blacklisting refresh token
- Users can create, update, delete their profile
- User can follow/unfollow other users and see the list 
of followers/followings in their profile
- Users can search users by first_name, last_name, country

#### Posts
- Authenticated users can create, update and delete their posts
- Authenticated users can see their posts and posts of users
they are following
- Authenticated users can like/unlike posts
- Users can see posts they liked in their profile
- Authenticated users can see and create comments to posts 
and delete their comments
- Authenticated users can schedule posts (with Celery)

## How to run with Docker

Docker should be installed.

Create `.env` file with your variables (look at `.env.sample`).

```shell
docker-compose build
docker-compose up
```


## How to run (without Docker)
Install PostgreSQL and create database.

1. Clone project and create virtual environment

```shell
git clone https://github.com/yuliia-stopkyna/social-media-api.git
cd social-media-api
python -m venv venv
source venv/bin/activate # on MacOS
venv\Scripts\activate # on Windows
pip install -r requirements.txt
```
2. Set environment variables

On Windows use ```export``` command instead of ```set```
```shell
set POSTGRES_HOST=<your db host>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db user>
set POSTGRES_PASSWORD=<your db password>
set DJANGO_SECRET_KEY=<your Django secret key>
```
3. Make migrations and run server

```shell
python manage.py migrate
python manage.py runserver
```

4. For scheduling posts and daily cleaning of expired refresh JWT tokens.

* Start redis server.
* Change `broker_url` in `social_media_api/celeryconfig.py` to localhost.

* Start celery worker as a separate process.
```shell
celery -A social_media_api worker --loglevel=info
``` 
* Start celery beat as a separate process.
```shell
celery -A social_media_api.celery beat -l info 
```
