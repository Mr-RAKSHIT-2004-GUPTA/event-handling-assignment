# 🧠 Event Management System (Django REST API)

This is a simple **Event Management System** built with **Django** and **Django REST Framework (DRF)**.  
It allows users to:
- Register and authenticate using JWT tokens.
- Create and manage events.
- RSVP to events.
- Write and view reviews for events.

---

## 🚀 Features

- User registration and authentication (JWT)
- CRUD operations for events
- RSVP system for event participation
- Review system for user feedback
- Role-based access (organizer vs participant)
- Paginated and filterable API endpoints

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Authentication:** JWT (using `rest_framework_simplejwt`)
- **Database:** SQLite (default)
- **Task Queue:** Celery + Redis (for async tasks)
- **Environment:** Python 3.9+ (recommended)

---

## ⚙️ Installation and Setup

###  Clone the repository
```bash
git clone <your_repo_url>
cd event_management
```
### Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # On Windows
# source venv/bin/activate   # On Mac/Linux
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create a superuser
```bash
python manage.py createsuperuser
```

### Run the development server
```bash
python manage.py runserver
```

Server will start at:
-> http://127.0.0.1:8000/

### Authentication (JWT)
Use these endpoints to get access and refresh tokens:
| Endpoint              | Method | Description          |
| --------------------- | ------ | -------------------- |
| `/api/token/`         | POST   | Obtain JWT tokens    |
| `/api/token/refresh/` | POST   | Refresh access token |

### Example (Obtain Token)
```bash
POST /api/token/
{
  "username": "admin",
  "password": "yourpassword"
}
```

### Example Response
```bash
{
  "access": "<your_access_token>",
  "refresh": "<your_refresh_token>"
}
```

### API Endpoints
| Endpoint                                 | Method    | Description            |
| ---------------------------------------- | --------- | ---------------------- |
| `/api/events/`                           | GET       | List all events        |
| `/api/events/`                           | POST      | Create new event       |
| `/api/events/{id}/`                      | GET       | Retrieve event details |
| `/api/events/{id}/`                      | PUT/PATCH | Update an event        |
| `/api/events/{id}/`                      | DELETE    | Delete an event        |
| `/api/events/{event_id}/rsvp/`           | POST      | RSVP to event          |
| `/api/events/{event_id}/rsvp/{user_id}/` | PUT       | Update RSVP            |
| `/api/events/{event_id}/reviews/`        | POST      | Add review             |
| `/api/token/`                            | POST      | Get JWT token          |
| `/api/token/refresh/`                    | POST      | Refresh token          |

### Project Structure
```bash
event_management/
│
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── events/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│
├── event_management/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md
```
### Testing API with Postman
1. Start the Django server.

2. Get JWT token using /api/token/.

3. Use the access token for authorization in subsequent requests.

4. Test event creation, RSVP, and review endpoints.

### Environment Variables
```bash
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```
### Author
Rakshit Gupta
Data Science Engineer | Django & AI Developer
📧 [rakshit2004gupta@gmail.com]

