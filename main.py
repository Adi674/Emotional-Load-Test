from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown"""
    # Startup
    print("🚀 Starting Emotional Load Test Microservice...")
    yield
    # Shutdown
    print("🛑 Shutting down Emotional Load Test Microservice...")


app = FastAPI(
    title="Emotional Load Test Microservice",
    description="Microservice for emotional load testing with async endpoints",
    version="1.0.0",
    debug=os.getenv("DEBUG") == "True",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "Emotional Load Test Microservice",
        "status": "active",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "emotional-test",
        "database": "connected"
    }