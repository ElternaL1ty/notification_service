![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)	![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)	![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
# Notification service
This project is a test task for FR. It is an implementation of a mailing service for users. Stack used: django+sqlite, celery+redis. The project task is at the [link](https://www.craft.do/s/n6OVYFVUpq0o6L)

### Completed side tasks:

- Task 3. Prepare docker-compose to start all project services with one command
- Task 5. Make it so that the page with Swagger UI opens at /docs/ and displays a description of the developed API
- Task 9.  The remote service may be unavailable, take a long time to respond to requests, or return incorrect responses. It is necessary to organize error handling and postponing requests in case of failure for subsequent resubmission. Delays in the work of the external service should not affect the work of the mailing service in any way.

Also this service is using JWT for API requests authentication

## Installation
First of all, clone this repository in the folder and open it in cmd

`git clone https://github.com/ElternaL1ty/notification_service.git`

Next steps can be done using Docker
### With Docker
- Create a superuser to get JWT token later

	`docker-compose run web python manage.py createsuperuser`
- Run the project

	`docker-compose up`
	
### Without docker
- Install all requirements using pip

	`pip3 install -r requirements.txt`
- Install redis ([here](https://redis.io/download/)) and run it

	`redis-server`
- Migrate django models and run django server

	`python manage.py makemigrations`

	`python manage.py migrate`

	`python manage.py runserver 0.0.0.0:8000`
- Run celery in new cmd tab

	`celery -A notification_service worker -P gevent --loglevel=INFO -E`
	
## API
This project provides API to control notifications, messages and clients. Full OpenAPI documentation you can see at http://hostname/docs/ after hosting django server
Note, that you can't get access to any API request without sending Bearer token in request headers. To obtain infinite-time JWT token, send POST request to http://hostname/api/token/ with this body:

    {
      "username": username,
      "password": password,
    }
## Feedback
- Mail: swaeami@gmail.com
- Telegram: @elternal1ty
