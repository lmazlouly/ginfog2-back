# FastAPI JWT Auth Boilerplate

A RESTful API boilerplate using FastAPI with JWT authentication, SQLAlchemy ORM, and proper API documentation. The application includes user management and waste reports functionality.

## Features

- FastAPI framework with automatic API documentation
- JWT Authentication with token generation and verification
- SQLAlchemy ORM for database operations
- MySQL database backend
- User management (registration, authentication, profile management)
- Waste reports tracking system with CRUD operations
- Role-based authorization (regular users vs superusers)
- Tagged API operations with operationId for frontend code generation
- Proper project structure with separation of concerns
- Dependency injection
- CORS support

## Project Structure

```
app/
├── api/              # API layer
│   ├── dependencies.py   # API dependencies (auth)
│   └── v1/              # API v1 endpoints
│       ├── auth/        # Authentication endpoints
│       ├── users/       # User management endpoints
│       └── waste_reports/ # Waste reports endpoints
├── core/             # Core modules
│   ├── config/       # App configuration
│   └── security/     # Security utilities
├── db/               # Database layer
│   ├── models/       # SQLAlchemy models
│   ├── repositories/ # Database repositories
│   └── session.py    # Database session
└── schemas/          # Pydantic schemas
main.py               # Application entry point
requirements.txt      # Python dependencies
.env                  # Environment variables
```

## Windows Setup Guide

### Prerequisites

- Python 3.8+ (recommended 3.10+)
- MySQL Server installed and running (or access to a MySQL database)
- Git

### Step 1: Clone the Repository

```bash
git clone [your-repository-url]
cd ginfog2-back
```

### Step 2: Set Up Python Virtual Environment

First you need to create virtual env for python using the following command for windows:

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

Next step activate the virtual env using the following command:

```bash
source venv/Scripts/activate
```

### Step 4: Install Dependencies

Now install dependencies on your virtual env using:

```bash
pip install -r requirements.txt
```

### Step 5: Configure the Database

1. Create a MySQL database named `ginfog2`
2. Create or update the `.env` file in the project root:

```
SECRET_KEY=dW5kZWZpbmVk
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=mysql://root:your_password@localhost:3306/ginfog2
PROJECT_NAME=FastAPI JWT Auth Boilerplate
API_V1_STR="/api/v1"
CORS_ORIGINS=["http://localhost:3000","http://localhost:3005"]
```

Replace `your_password` with your MySQL root password or use appropriate credentials.

### Step 6: Database Setup

The application automatically initializes the database tables when it first runs. However, if you need more control over migrations, you can use Alembic (which is included in the requirements):

```bash
# To create a new migration (after making model changes)
venv\Scripts\alembic revision --autogenerate -m "Description of changes"

# To apply migrations
venv\Scripts\alembic upgrade head
```

### Step 7: Run the Application

When the installation finishes, you can run the project using this command:

```bash
uvicorn main:app --reload --port=3005
```

OR
```bash
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port=3005
```

### Step 8: Access the API Documentation

Open your browser and navigate to:
- http://localhost:3005/docs (Swagger UI)
- http://localhost:3005/redoc (ReDoc)

## API Documentation

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/auth/register` | POST | Register a new user | No |
| `/api/v1/auth/login` | POST | Log in and get JWT token | No |

### User Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/users/me` | GET | Get current user profile | Yes |
| `/api/v1/users/me` | PUT | Update current user profile | Yes |
| `/api/v1/users` | GET | Get list of users (superusers only) | Yes |
| `/api/v1/users/{user_id}` | GET | Get user by ID (superusers only) | Yes |
| `/api/v1/users/{user_id}` | PUT | Update user (superusers only) | Yes |

### Waste Reports Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/waste-reports` | POST | Create a new waste report | Yes |
| `/api/v1/waste-reports` | GET | Get list of waste reports (users see only their reports; superusers see all) | Yes |
| `/api/v1/waste-reports/{waste_report_id}` | GET | Get waste report by ID | Yes |
| `/api/v1/waste-reports/{waste_report_id}` | PUT | Update waste report | Yes |
| `/api/v1/waste-reports/{waste_report_id}` | DELETE | Delete waste report | Yes |

## Authentication Flow

1. **Register**: Create a new user account with the `/api/v1/auth/register` endpoint
   ```json
   {
     "email": "user@example.com",
     "password": "strongpassword",
     "full_name": "John Doe"
   }
   ```

2. **Login**: Authenticate and get JWT token with the `/api/v1/auth/login` endpoint
   ```json
   {
     "username": "user@example.com",
     "password": "strongpassword"
   }
   ```
   The response will contain the access token:
   ```json
   {
     "access_token": "eyJhbG...[token]",
     "token_type": "bearer"
   }
   ```

3. **Use Token**: Include the JWT token in the Authorization header as `Bearer {token}` for protected endpoints

## Troubleshooting Windows-Specific Issues

### MySQL Connection Issues

If you encounter database connection issues:

1. Verify your MySQL server is running
2. Check the connection string in the `.env` file
3. Ensure you've created the `ginfog2` database
4. Try using the PyMySQL driver by modifying the DATABASE_URL:
   ```
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/ginfog2
   ```

### Python Path Issues

If you encounter import errors, ensure your Python path is correct by running the application with the full path to the Python interpreter in your virtual environment.

## Waste Reports Feature

### Overview

The waste reports feature allows users to submit and track waste collection reports. Each report includes:

- Location information
- Waste type
- Quantity
- Status tracking (pending, processing, completed, rejected)
- Submission date

### Data Model

```python
class WasteReport:
    id: int
    location: str
    waste_type: str
    quantity: float
    status: str  # One of: "pending", "processing", "completed", "rejected"
    user_id: int
    date: datetime
```

### Example Usage

#### Creating a waste report

```python
import requests

url = "http://localhost:8000/api/v1/waste-reports"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "location": "123 Main St",
    "waste_type": "plastic",
    "quantity": 5.75
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### Getting waste reports for the authenticated user

```python
import requests

url = "http://localhost:8000/api/v1/waste-reports"
headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}

response = requests.get(url, headers=headers)
print(response.json())
```

### Authorization Rules

- Regular users can only see, edit, and delete their own reports
- Superusers can see, edit, and delete all reports
- Authentication is required for all waste report operations

## Frontend Integration

This API is designed to work well with frontend code generation tools like pnpm orval. Each endpoint has:

- Proper tags for grouping 
- Descriptive operationId for function naming
- Response models for type safety

## License

This project is licensed under the MIT License.
