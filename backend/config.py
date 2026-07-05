"""
Smriti Configuration
Manages environment variables and application settings

Smriti is a memory-aware field service dispatch system.
"""
import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings

# macOS python.org builds ship without default CA certificates, which breaks
# TLS to Cognee Cloud (CERTIFICATE_VERIFY_FAILED). Point Python's SSL stack
# at certifi's CA bundle unless the environment already provides one.
if not os.environ.get("SSL_CERT_FILE"):
	try:
		import certifi
		os.environ["SSL_CERT_FILE"] = certifi.where()
	except ImportError:
		pass


class Settings(BaseSettings):
	"""Application settings loaded from environment variables"""

	# Application
	APP_NAME: str = "Smriti"
	APP_SUBTITLE: str = "Memory-aware dispatch for Indian field operations"
	APP_VERSION: str = "0.1.0"
	DEBUG: bool = True
	ENVIRONMENT: str = "development"

	# ── Cognee Cloud (Smriti memory layer) ─────────────────────────
	# COGNEE_ENABLED=true + COGNEE_API_KEY are required for the memory
	# endpoints to work. Without them, /api/v1/memory/* returns a clear
	# configuration error while the base dispatch app keeps working.
	COGNEE_ENABLED: bool = False
	COGNEE_API_KEY: Optional[str] = None
	# URL of the Cognee Cloud (or self-hosted Cognee) instance. When set,
	# cognee.serve(url=..., api_key=...) routes all memory operations to it.
	# When empty but COGNEE_ENABLED=true, the SDK runs cognee locally
	# (requires LLM_API_KEY for its internal pipeline).
	COGNEE_CLOUD_URL: Optional[str] = None
	# Dataset names inside Cognee — customer-specific memories live in
	# per-customer datasets so `forget` can remove them while the
	# anonymized operational patterns dataset survives.
	COGNEE_OPS_DATASET: str = "crewmind_ops_patterns"
	COGNEE_CUSTOMER_DATASET_PREFIX: str = "crewmind_customer_"

	# Database - PostgreSQL (SQLite fallback supported for keyless local demo)
	DATABASE_URL: str = "postgresql://smriti:smriti@localhost:5432/smriti"
	DATABASE_ECHO: bool = False  # Set to True to see SQL queries in console

	# API
	API_HOST: str = "0.0.0.0"
	API_PORT: int = 8000
	API_RELOAD: bool = True
	API_V1_PREFIX: str = "/api/v1"

	# CORS
	CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

	# Routing Constants
	DEFAULT_TRAVEL_SPEED_MPH: float = 30.0  # Average speed for travel time calculations
	MAX_JOBS_PER_TECH: int = 8  # Maximum jobs per technician per day
	WORK_DAY_START_HOUR: int = 8  # 8 AM
	WORK_DAY_END_HOUR: int = 17  # 5 PM

	# Job Duration Estimates (in minutes)
	DEFAULT_JOB_DURATION: int = 60
	INSTALL_DURATION: int = 90
	REPAIR_DURATION: int = 45
	MAINTENANCE_DURATION: int = 30
	INSPECTION_DURATION: int = 30

	# Distance Calculation
	MILES_PER_DEGREE_LAT: float = 69.0  # Approximate miles per degree latitude
	MILES_PER_DEGREE_LON: float = 54.6  # Approximate miles per degree longitude (at 40° latitude)

	class Config:
		env_file = ".env"
		case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
	"""Get cached settings instance"""
	return Settings()
