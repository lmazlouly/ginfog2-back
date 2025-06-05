# FastAPI JWT Auth Boilerplate

A RESTful API boilerplate using FastAPI with JWT authentication, SQLAlchemy ORM, and proper API documentation.

## Features

- FastAPI framework with automatic API documentation
- JWT Authentication
- SQLAlchemy ORM
- Tagged API operations with operationId for frontend code generation (e.g., pnpm orval)
- Proper project structure with separation of concerns
- Dependency injection

## Project Structure

```
app/
├── api/              # API layer
│   ├── dependencies.py   # API dependencies (auth)
│   └── v1/              # API v1 endpoints
│       ├── auth/        # Authentication endpoints
│       └── users/       # User management endpoints
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
```

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash (Windows, Linux & MacOS)
uvicorn main:app --reload
```

OR via venv directly (Windows):

```bash
./venv/Scripts/python.exe -m uvicorn main:app --reload
```

OR (Linux/MacOS):

```bash
./venv/bin/python -m uvicorn main:app --reload
```

4. Open your browser and navigate to http://localhost:8000/docs to see the API documentation.

## Authentication Flow

1. Register a new user using the `/api/v1/auth/register` endpoint
2. Login with email and password using the `/api/v1/auth/login` endpoint
3. Use the returned JWT token in the Authorization header as `Bearer {token}` for protected endpoints

## Frontend Integration

This API is designed to work well with frontend code generation tools like pnpm orval. Each endpoint has:

- Proper tags for grouping 
- Descriptive operationId for function naming
- Response models for type safety

## Configuration

All configuration is loaded from environment variables or `.env` file:

```
SECRET_KEY=dW5kZWZpbmVk
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=mysql://root:@localhost:3306/ginfog2
PROJECT_NAME=FastAPI JWT Auth Boilerplate
API_V1_STR="/api/v1"
CORS_ORIGINS=["http://localhost:3000","http://localhost:3005"]
```

## License

This project is licensed under the MIT License.
