"""
Smriti Main API Application
Memory-aware dispatch for Indian field operations.

Built with the Smriti Cognee memory layer.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.database.connection import init_db
from backend.api.routes import technicians, jobs, assignments, routing, memory, demo

logger = logging.getLogger(__name__)
settings = get_settings()


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
SERVE_FRONTEND = FRONTEND_DIST.is_dir() and (FRONTEND_DIST / "index.html").is_file()


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Handle startup and shutdown events"""
	await init_db()
	print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started — {settings.APP_SUBTITLE}")
	print(f"📄 API Documentation: http://localhost:{settings.API_PORT}/docs")
	# First run on an empty database: seed the Delhi NCR demo data so the
	# console opens populated — no seed buttons needed in the UI.
	from sqlalchemy import select, func
	from backend.database.connection import AsyncSessionLocal
	from backend.database.models import Technician
	async with AsyncSessionLocal() as session:
		tech_count = (await session.execute(select(func.count(Technician.id)))).scalar_one()
	if tech_count == 0:
		from backend.database.seeds.seed_data import seed_all
		await seed_all()
		print("🌱 Empty database — Delhi NCR demo data auto-seeded")
	# Connect the Cognee memory layer (never blocks startup on failure —
	# /api/v1/memory/status reports configuration problems clearly)
	from backend.services.cognee_memory import init_cognee
	cognee_status = await init_cognee()
	if cognee_status.get("initialized"):
		print("🧠 Cognee memory layer connected")
	else:
		print(f"🧠 Cognee memory layer inactive: {cognee_status.get('reason', 'not configured')}")
	yield
	print(f"🛑 {settings.APP_NAME} shutting down")


app = FastAPI(
	title=settings.APP_NAME,
	description=(
		"Memory-aware dispatch for Indian field operations. "
		"Built with the Cognee Cloud memory layer."
	),
	version=settings.APP_VERSION,
	docs_url="/docs",
	redoc_url="/redoc",
	lifespan=lifespan,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.CORS_ORIGINS,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


if not SERVE_FRONTEND:
	@app.get("/")
	async def root():
		return {
			"message": f"Welcome to {settings.APP_NAME} API",
			"version": settings.APP_VERSION,
			"docs": "/docs",
			"status": "operational",
		}


@app.get("/health")
async def health_check():
	return {
		"status": "healthy",
		"version": settings.APP_VERSION,
	}


# Routers
app.include_router(
	technicians.router,
	prefix=f"{settings.API_V1_PREFIX}/technicians",
	tags=["Technicians"],
)

app.include_router(
	jobs.router,
	prefix=f"{settings.API_V1_PREFIX}/jobs",
	tags=["Jobs"],
)

app.include_router(
	assignments.router,
	prefix=f"{settings.API_V1_PREFIX}/assignments",
	tags=["Assignments"],
)

app.include_router(
	routing.router,
	prefix=f"{settings.API_V1_PREFIX}/routing",
	tags=["Routing"],
)

app.include_router(
	memory.router,
	prefix=f"{settings.API_V1_PREFIX}/memory",
	tags=["Memory (Cognee)"],
)

app.include_router(
	demo.router,
	prefix=f"{settings.API_V1_PREFIX}/demo",
	tags=["Demo"],
)


# SPA fallback — must be registered AFTER all /api/* routers so they win on prefix.
# StaticFiles with html=True serves index.html at "/" and assets by path.
# A catch-all FileResponse handles client-side routes (e.g. /jobs/123 deep-links).
if SERVE_FRONTEND:
	app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

	@app.get("/{full_path:path}", include_in_schema=False)
	async def spa_fallback(full_path: str):
		candidate = FRONTEND_DIST / full_path
		if full_path and candidate.is_file():
			return FileResponse(candidate)
		return FileResponse(FRONTEND_DIST / "index.html")


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"backend.api.main:app",
		host=settings.API_HOST,
		port=settings.API_PORT,
		reload=settings.API_RELOAD,
	)
