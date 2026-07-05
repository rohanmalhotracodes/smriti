"""
Smriti — /api/v1/demo routes: demo-day controls.

Part of the Smriti Cognee memory layer.

These endpoints drive the scripted hackathon demo:
  - seed the Delhi NCR dispatch data
  - inject the 10:47 VIP HVAC emergency at MetroCare Tower
  - reset the demo day
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database.models import Job, JobStatus
from backend.services.memory_hooks import remember_event

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/seed-india")
async def seed_india_dispatch_data():
	"""Reset the database and seed the Delhi NCR technicians + today's jobs."""
	from backend.database.seeds.seed_data import seed_all, TECHNICIANS, make_jobs
	try:
		await seed_all()
	except Exception as e:  # noqa: BLE001
		raise HTTPException(status_code=500, detail=f"Seed failed: {e}")
	return {
		"success": True,
		"message": "Delhi NCR demo data seeded.",
		"technicians": len(TECHNICIANS),
		"jobs": len(make_jobs()),
	}


@router.post("/inject-vip")
async def inject_vip_emergency(db: AsyncSession = Depends(get_db)):
	"""
	Inject the scripted 10:47 AM VIP emergency:
	HVAC failure at MetroCare Tower, Cyber City, Gurugram —
	"Server room temperature rising; previous cooling issue returned".
	"""
	from backend.database.seeds.seed_data import VIP_EMERGENCY_JOB

	existing = await db.execute(
		select(Job).where(Job.job_number == VIP_EMERGENCY_JOB["job_number"])
	)
	job = existing.scalar_one_or_none()
	if job and job.status not in (JobStatus.CANCELLED,):
		return {
			"success": True,
			"already_exists": True,
			"job_id": job.id,
			"message": "VIP emergency already injected.",
		}

	now = datetime.now(timezone.utc)
	injected_at = now.replace(hour=10, minute=47, second=0, microsecond=0)
	job = Job(
		**VIP_EMERGENCY_JOB,
		status=JobStatus.PENDING,
		scheduled_date=injected_at,
	)
	db.add(job)
	await db.commit()
	await db.refresh(job)

	remember_event(
		"job_created", job.id,
		notes="10:47 AM VIP emergency injected: server room temperature rising; previous cooling issue returned.",
	)
	return {
		"success": True,
		"already_exists": False,
		"job_id": job.id,
		"job_number": job.job_number,
		"message": "🚨 10:47 AM VIP emergency injected — HVAC failure at MetroCare Tower, Cyber City.",
	}


@router.post("/reset")
async def reset_demo():
	"""Full demo reset — wipe and re-seed the Delhi NCR dispatch data."""
	from backend.database.seeds.seed_data import seed_all
	try:
		await seed_all()
	except Exception as e:  # noqa: BLE001
		raise HTTPException(status_code=500, detail=f"Reset failed: {e}")
	return {"success": True, "message": "Demo reset — fresh Delhi NCR day seeded. (Cognee memory is kept; use the forget demo to remove customer memory.)"}


@router.get("/status")
async def demo_status(db: AsyncSession = Depends(get_db)):
	"""Demo state: is the VIP job injected / assigned / completed?"""
	from backend.database.seeds.seed_data import VIP_EMERGENCY_JOB
	result = await db.execute(
		select(Job).where(Job.job_number == VIP_EMERGENCY_JOB["job_number"])
	)
	vip = result.scalar_one_or_none()
	return {
		"vip_injected": vip is not None,
		"vip_job_id": vip.id if vip else None,
		"vip_status": vip.status.value if vip else None,
		"vip_assigned_to": vip.assignment.technician.name if vip and vip.assignment else None,
	}
