"""
Smriti — /api/v1/memory routes (Cognee Cloud memory layer).

Part of the Smriti Cognee memory layer.

Every endpoint here talks to REAL Cognee (remember/recall/improve/forget).
If Cognee is not configured the endpoints return HTTP 503 with a clear
configuration message — there is no fake in-memory fallback.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database.models import MemoryEvent, Technician
from backend.logic import jobs as job_logic
from backend.logic import technicians as tech_logic
from backend.logic.routing import memory_router
from backend.services import cognee_memory, memory_seed
from backend.services.cognee_memory import CogneeNotConfigured, job_category, route_area_name

router = APIRouter()


def _cognee_http_error(e: Exception) -> HTTPException:
	if isinstance(e, CogneeNotConfigured):
		return HTTPException(status_code=503, detail=str(e))
	return HTTPException(status_code=502, detail=f"Cognee operation failed: {e}")


# ── Request models ───────────────────────────────────────────────────────────

class RememberJobRequest(BaseModel):
	event_type: str = Field(default="manual_snapshot", max_length=50)
	notes: Optional[str] = Field(None, max_length=1000)


class ImproveJobRequest(BaseModel):
	actual_duration_minutes: Optional[int] = None
	arrival_delay_minutes: Optional[int] = None
	resolution_notes: Optional[str] = None
	parts_used: Optional[str] = None
	customer_rating: Optional[int] = Field(None, ge=1, le=5)
	fix_type: Optional[str] = Field(None, pattern="^(temporary|permanent|workaround)$")
	watch_recurrence: Optional[bool] = None


class OverrideMemoryRequest(BaseModel):
	assigned_technician_id: int
	recommended_technician_id: Optional[int] = None
	reason: str = Field(..., max_length=300)


class ForgetCustomerRequest(BaseModel):
	customer_name: str = Field(..., min_length=1, max_length=100)
	confirm: bool = False


# ── Status / health ─────────────────────────────────────────────────────────

@router.get("/status")
async def memory_status():
	"""Cognee configuration status + last successful memory operation."""
	return await cognee_memory.memory_healthcheck()


# ── Seeding historical memory ────────────────────────────────────────────────

@router.post("/seed-india")
async def seed_india_memories(db: AsyncSession = Depends(get_db)):
	"""
	Seed the India-specific synthetic historical memories into Cognee.

	Writes 40+ structured job-history and site-note records: full detail
	into per-customer datasets, anonymized copies into the shared
	ops-patterns dataset. This can take a few minutes — Cognee runs its
	knowledge-graph pipeline (cognify) on every dataset.
	"""
	texts_by_dataset = memory_seed.build_seed_texts()
	try:
		stored = await cognee_memory.remember_texts(db, texts_by_dataset, event_type="memory_seed_india")
	except CogneeNotConfigured as e:
		raise _cognee_http_error(e)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)
	return {
		"success": True,
		"message": (
			f"Seeded {memory_seed.seed_record_count()} synthetic historical memories "
			f"across {len(stored)} Cognee datasets."
		),
		"records": memory_seed.seed_record_count(),
		"datasets": stored,
	}


# ── Per-job memory operations ────────────────────────────────────────────────

@router.post("/jobs/{job_id}/remember")
async def remember_job(job_id: int, body: RememberJobRequest, db: AsyncSession = Depends(get_db)):
	"""Manually remember the current job state as a memory event."""
	job = await job_logic.get_job(db, job_id)
	if not job:
		raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
	technician = None
	if job.assignment:
		technician = await tech_logic.get_technician(db, job.assignment.technician_id)
	try:
		result = await cognee_memory.remember_job_event(
			db, body.event_type, job, technician, job.assignment, notes=body.notes,
		)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)
	return {"success": True, **result}


@router.get("/jobs/{job_id}/insights")
async def job_insights(job_id: int, db: AsyncSession = Depends(get_db)):
	"""
	The Memory Insight panel payload: recalled similar jobs, site history,
	technician risk, recommended technician, and suggested dispatcher note.
	"""
	job = await job_logic.get_job(db, job_id)
	if not job:
		raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
	try:
		recall = await cognee_memory.recall_job_context(job)
		route_result = await memory_router.memory_aware_route(db, job_id, recall=recall)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)

	records = recall["records"]
	category = job_category(job)
	area = route_area_name(job.route_criteria)
	site_lower = job.customer_name.lower()

	events = [r for r in records if r.get("record_type") == "FIELD_JOB_EVENT"]
	similar = [
		r for r in events
		if (r.get("job_type") or "").lower() == category.lower()
		and (r.get("route_area") or "").lower() == area.lower()
	]
	site_history = [r for r in events if (r.get("site") or "").lower() == site_lower]
	site_notes = [r for r in records if r.get("record_type") == "SITE_NOTE"
	              and (r.get("site") or "").lower() == site_lower]
	access_notes = [n for n in site_notes if "access" in (n.get("note_type") or "")]
	reopened_here = [r for r in site_history if (r.get("reopened") or "").lower() == "yes"]

	candidates = route_result.get("scoring_breakdown", []) if route_result.get("has_match") else []
	base = route_result.get("base_router_technician") if route_result.get("has_match") else None
	best = route_result.get("recommended_technician") if route_result.get("has_match") else None
	base_candidate = next((c for c in candidates if base and c["technician_id"] == base["technician_id"]), None)
	best_candidate = next((c for c in candidates if best and c["technician_id"] == best["technician_id"]), None)

	badges = []
	if len(similar) >= 2 or len(reopened_here) >= 1:
		badges.append({"key": "repeat_issue", "label": "Repeat Issue",
		               "detail": f"{len(similar)} similar {category} incident(s) recalled in {area}"})
	if access_notes:
		badges.append({"key": "access_risk", "label": "Access Risk",
		               "detail": f"{len(access_notes)} access delay memory(ies) at {job.customer_name}"})
	if base_candidate and base_candidate["stats"]["overruns"] >= 2:
		badges.append({"key": "overrun_risk", "label": "Technician Overrun Risk",
		               "detail": f"{base_candidate['technician_name']}: {base_candidate['stats']['overruns']} overruns on {category}"})
	if best_candidate and best_candidate["site_familiarity"] != "low":
		badges.append({"key": "site_familiarity", "label": "Site Familiarity",
		               "detail": f"{best_candidate['technician_name']} knows {job.customer_name} ({best_candidate['stats']['site_visits']} visit(s))"})
	if job.priority == 1:
		badges.append({"key": "vip", "label": "VIP Priority", "detail": "Priority-1 emergency job"})
	if route_result.get("recommendation_changed"):
		badges.append({"key": "recommended_by_memory", "label": "Recommended by Memory",
		               "detail": f"Memory recommends {best['technician_name']} over the base router's choice"})

	return {
		"job_id": job.id,
		"job_number": job.job_number,
		"customer_name": job.customer_name,
		"route_area": area,
		"job_category": category,
		"is_repeat_issue": len(similar) >= 2 or len(reopened_here) >= 1,
		"repeat_summary": (
			f"{len(similar)} similar {category} incident(s) recalled in {area}; "
			f"{len(reopened_here)} previous fix(es) at this site reopened."
		),
		"similar_jobs": similar[:8],
		"site_history": site_history[:8],
		"site_notes": site_notes[:4],
		"badges": badges,
		"technician_insights": candidates,
		"base_router_technician": base,
		"recommended_technician": best,
		"recommendation_changed": route_result.get("recommendation_changed", False),
		"risk_level": route_result.get("risk_level"),
		"confidence_score": route_result.get("confidence_score"),
		"explanation": route_result.get("explanation"),
		"suggested_dispatch_note": route_result.get("suggested_dispatch_note"),
		"recalled_memories": recall["chunks"][:12],
		"memories_recalled": len(records),
	}


@router.get("/jobs/{job_id}/technicians/{tech_id}/scorecard")
async def technician_scorecard(job_id: int, tech_id: int, db: AsyncSession = Depends(get_db)):
	"""This technician's recalled past performance for this job type/site/area."""
	job = await job_logic.get_job(db, job_id)
	if not job:
		raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
	tech = await tech_logic.get_technician(db, tech_id)
	if not tech:
		raise HTTPException(status_code=404, detail=f"Technician {tech_id} not found")
	try:
		context = await cognee_memory.recall_technician_context(job, tech)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)
	records = context["records"]
	stats = memory_router._tech_stats(tech, job, records)  # noqa: SLF001 — same package family
	return {
		"job_id": job.id,
		"technician_id": tech.id,
		"technician_name": tech.name,
		"job_category": job_category(job),
		"route_area": route_area_name(job.route_criteria),
		"stats": {k: v for k, v in stats.items() if k != "evidence"},
		"records": records[:10],
		"recall_query": context["query"],
	}


@router.post("/jobs/{job_id}/improve")
async def improve_job_memory(job_id: int, body: ImproveJobRequest, db: AsyncSession = Depends(get_db)):
	"""
	Post-completion learning: remember the outcome and run cognee.improve()
	to consolidate the graph. Called after a job completes.
	"""
	job = await job_logic.get_job(db, job_id)
	if not job:
		raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
	technician = None
	if job.assignment:
		technician = await tech_logic.get_technician(db, job.assignment.technician_id)

	outcome = {k: v for k, v in body.model_dump().items() if v is not None}
	outcome.setdefault("result", "resolved")
	if body.fix_type:
		outcome["result"] = f"{'successful permanent fix' if body.fix_type == 'permanent' else body.fix_type + ' fix'}"
	try:
		result = await cognee_memory.improve_after_job_completion(db, job, technician, outcome)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)
	return {
		"success": True,
		"message": "Cognee learned from this job.",
		**result,
	}


@router.post("/jobs/{job_id}/override")
async def remember_override(job_id: int, body: OverrideMemoryRequest, db: AsyncSession = Depends(get_db)):
	"""
	Remember a dispatcher override of the memory-aware recommendation.
	Stored as a DISPATCH_OVERRIDE memory; improved with the real outcome
	when the job later completes.
	"""
	job = await job_logic.get_job(db, job_id)
	if not job:
		raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
	assigned = await tech_logic.get_technician(db, body.assigned_technician_id)
	recommended = (
		await tech_logic.get_technician(db, body.recommended_technician_id)
		if body.recommended_technician_id else None
	)
	if not assigned:
		raise HTTPException(status_code=404, detail="Assigned technician not found")

	note = (
		f"Dispatcher assigned {assigned.name}"
		+ (f" instead of memory-recommended {recommended.name}" if recommended else "")
		+ f" because: {body.reason}. Outcome pending."
	)
	try:
		result = await cognee_memory.remember_job_event(
			db, "dispatch_override", job, assigned, job.assignment,
			outcome={"result": "override — outcome pending"},
			notes=note,
		)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)
	return {"success": True, "override_note": note, **result}


# ── Privacy: forget a customer ───────────────────────────────────────────────

@router.post("/customers/forget")
async def forget_customer(body: ForgetCustomerRequest, db: AsyncSession = Depends(get_db)):
	"""
	Privacy demo — cognee.forget() the customer's dataset. Customer/site
	specific memories are deleted; anonymized ops patterns survive.
	"""
	if not body.confirm:
		raise HTTPException(
			status_code=400,
			detail="Confirmation required: pass confirm=true to forget customer memory.",
		)
	try:
		result = await cognee_memory.forget_customer_memory(db, body.customer_name)
	except Exception as e:  # noqa: BLE001
		raise _cognee_http_error(e)
	return {"success": True, **result}


# ── Local audit log ──────────────────────────────────────────────────────────

@router.get("/events")
async def memory_events(
	limit: int = Query(50, ge=1, le=500),
	db: AsyncSession = Depends(get_db),
):
	"""Local audit trail of what was sent to Cognee (demo transparency)."""
	result = await db.execute(
		select(MemoryEvent).order_by(MemoryEvent.created_at.desc(), MemoryEvent.id.desc()).limit(limit)
	)
	events = result.scalars().all()
	return [
		{
			"id": e.id,
			"event_type": e.event_type,
			"job_id": e.job_id,
			"technician_id": e.technician_id,
			"customer_name": e.customer_name,
			"site_name": e.site_name,
			"route_area": e.route_area,
			"payload_preview": (e.payload_preview or "")[:400],
			"cognee_status": e.cognee_status,
			"created_at": e.created_at.isoformat() if e.created_at else None,
		}
		for e in events
	]
