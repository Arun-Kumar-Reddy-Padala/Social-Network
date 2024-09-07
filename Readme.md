# Django Social Network Project

A social networking web application built with Django and Docker.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Using Docker](#using-docker)
- [Usage](#usage)
- [Automatic Logout Configuration](#automatic-logout-configuration)
- [Testing](#testing)

## Features

- User signup, login, and logout
- Friend request system (send, accept, reject requests)
- Paginated list of friends and search functionality
- Dockerized setup for easy deployment

## Requirements

- Python 3.9+
- Django 3.2+
- Docker (optional, for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repository-url.git
cd your-repository-folder

2. Create a Virtual Environment and Activate It

Create a virtual environment to manage dependencies.

# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\\Scripts\\activate

3. Install Dependencies

Install the required packages listed in the requirements.txt file.

pip install -r requirements.txt


4. Run Database Migrations

Run Django’s migrations to set up the database.

python manage.py makemigrateions
python manage.py migrate


5. Create a Superuser (Optional)

Create an admin account to access the Django admin panel.
python manage.py createsuperuser

Follow the prompts to set up your superuser credentials.


6. Collect Static Files

python manage.py collectstatic --noinput


7. Run the Development Server

python manage.py runserver

You can now access the application at http://127.0.0.1:8000/.



Using Docker

You can containerize the application using Docker. The following steps assume Docker is installed on your system.

1. Build and Run with Docker Compose

docker-compose up --build

This will build the Docker image, create containers for the Django application, and start the development server.


2. Access the Application

Once Docker Compose is running, you can access the application in your browser at http://127.0.0.1:8000/.


3. Stop the Containers

To stop the containers, press CTRL+C in the terminal or run:

docker-compose down


Usage

1. Login and Signup

    Navigate to the signup page (/signup/) to create a new user account.
    After signing up, log in using the credentials you provided.

2. Friend Request System

    Send friend requests by searching for users by name or email.
    Accept or reject incoming friend requests from the dashboard.
    View your list of friends with pagination.

3. Search Functionality

    Use the search feature to find users by exact email or partial name match.


Testing

To run unit tests for your Django app:

python manage.py test


You can also run tests within the Docker container:

docker-compose run web python manage.py test
