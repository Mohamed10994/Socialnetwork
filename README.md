# Socialnetwork

## About

* A simple Django App that allows registered users to post social/posts to their profiles, with the option to update/delete their posts.
* The app has a following/followers system where the user can choose whose posts should appear on their homepage.
* Comments system on users' posts, with the option to update/delete their comments.
* Like/Unlike system on users's posts.
* Notifications for user's new comments, reply, likes, messages and following.

---

## Prerequisites

1. Front End:
    * HTML (Jinja2)
    * CSS
    * Javascript (JQuery)
    * Bootstrap
2. Back End (Python3.6.x):
    * Django 4.1.3.
    * django-Crispy-forms
    * Django-Notifications

---

## Installation

1. `https://github.com/Mohamed10994/Socialnetwork.git` to clone the app from GitHub.com.
2. `python3 -m venv socialnetwork_venv` to create a new virtual environment.
3. `source socialnetwork_venv/Scripts/activate` to activate the virtual environment.
4. `pip install -r requirements.txt` to install the required software.
5. `python manage.py makemigrations` to set the database migrations.
6. `python manage.py migrate` to run the database migrations.
7. `python manage.py runserver` to run the server on the default port.

The app will run on <http://127.0.0.1:8000> (<http://localhost:8000>) by default.

---

## Screenshots of the website

1. Home Page.
    ![Home](/social/static/social/screenshots/1.JPG)

2. My own Profile.
    ![My Profile](/social/static/social/screenshots/2.JPG)

3. Profile Page of a profile I am following.
    ![My Profile](/social/static/social/screenshots/3.JPG)

4. Profile Followers page.
    ![My Profile](/social/static/social/screenshots/4.JPG)

5. Notifications and Messages List.
    ![My Profile](/social/static/social/screenshots/5.JPG)

6. Chat Between Two Users.
    ![My Profile](/social/static/social/screenshots/6.JPG)

---
