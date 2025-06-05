import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.waste_reports.router import router as waste_reports_router
from app.core.config.settings import settings
from app.db.models.user import User  # Import models to register with SQLAlchemy
from app.db.models.waste_report import WasteReport  # Import waste report model
from app.db.session import Base, engine

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Boilerplate with JWT Authentication",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(waste_reports_router)


@app.get("/", tags=["status"], operation_id="getStatus")
def read_root():
    return {"message": "Welcome to FastAPI JWT Auth Boilerplate"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3005, reload=True)
