"""
Smriti — memory-aware routing.

Part of the Smriti Cognee memory layer.

Keeps the existing base router untouched and adds a `memory_aware` mode:

	base_score      — from the existing route logic (distance-driven,
	                  closest qualified tech scores highest)
	memory modifiers — computed from REAL Cognee recall results, parsed
	                  from the structured FIELD_JOB_EVENT / SITE_NOTE
	                  records Smriti stores via cognee.remember()

The output is deliberately NOT a black box: every candidate carries its
scoring breakdown (modifier, points, and the memory evidence behind it)
so the UI can show exactly why the recommendation changed.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Job, Technician
from backend.logic import jobs as job_logic
from backend.logic import technicians as tech_logic
from backend.logic.routing.distance import haversine_distance
from backend.services import cognee_memory
from backend.services.cognee_memory import job_category, route_area_name

MILES_TO_KM = 1.60934

# Memory scoring model — points per modifier (documented in README)
MOD_SIMILAR_AREA_SUCCESS = +25   # successful similar jobs in same route area
MOD_SITE_SUCCESS = +20           # successful history at same site/customer
MOD_SKILL_SUCCESS = +12          # skill-specific success for this job category
MOD_REPEAT_OVERRUNS = -30        # repeated overruns on same job category
MOD_CUSTOMER_COMPLAINT = -25     # previous complaint (rating <= 2) at same site
MOD_TEMPORARY_FIX = -20          # previous fix by tech was temporary/reopened
MOD_UNKNOWN_ON_VIP = -15         # tech unknown to memory on a VIP/priority-1 job
MOD_ACCESS_RISK = -10            # site has access-delay memory, tech unfamiliar


def _is_success(record: dict) -> bool:
	result = (record.get("result") or record.get("outcome") or "").lower()
	return "successful" in result or ("resolved" in result and record.get("overran") != "yes")


def _is_category_match(record: dict, category: str) -> bool:
	return (record.get("job_type") or "").strip().lower() == category.strip().lower()


def _tech_stats(tech: Technician, job: Job, records: list[dict]) -> dict:
	"""Aggregate this technician's memory evidence for this job."""
	category = job_category(job)
	area = route_area_name(job.route_criteria)
	site = job.customer_name.lower()

	tech_records = [
		r for r in records
		if r.get("record_type") == "FIELD_JOB_EVENT"
		and (r.get("technician") or "").strip().lower() == tech.name.strip().lower()
	]
	cat_records = [r for r in tech_records if _is_category_match(r, category)]

	similar_area_success = [
		r for r in cat_records
		if _is_success(r) and (r.get("route_area") or "").strip().lower() == area.strip().lower()
	]
	site_records = [r for r in tech_records if (r.get("site") or "").strip().lower() == site]
	site_success = [r for r in site_records if _is_success(r)]
	skill_success = [r for r in cat_records if _is_success(r)]
	overruns = [r for r in cat_records if (r.get("overran") or "").lower() == "yes"]
	complaints = [
		r for r in site_records
		if str(r.get("customer_rating", "")).strip() in ("1", "2")
	]
	temporary = [
		r for r in tech_records
		if ((r.get("reopened") or "").lower() == "yes"
			or "temporary" in (r.get("result") or r.get("outcome") or "").lower())
		and ((r.get("site") or "").strip().lower() == site or _is_category_match(r, category))
	]
	return {
		"total_memories": len(tech_records),
		"similar_area_success": len(similar_area_success),
		"site_success": len(site_success),
		"site_visits": len(site_records),
		"skill_success": len(skill_success),
		"overruns": len(overruns),
		"complaints": len(complaints),
		"temporary_fixes": len(temporary),
		"evidence": {
			"similar_area_success": [r.get("raw", "")[:220] for r in similar_area_success[:3]],
			"overruns": [r.get("raw", "")[:220] for r in overruns[:3]],
			"complaints": [r.get("raw", "")[:220] for r in complaints[:2]],
			"temporary_fixes": [r.get("raw", "")[:220] for r in temporary[:2]],
		},
	}


def _site_access_notes(job: Job, records: list[dict]) -> list[dict]:
	"""Unresolved access-delay memories for this job's site."""
	site = job.customer_name.lower()
	return [
		r for r in records
		if r.get("record_type") == "SITE_NOTE"
		and (r.get("site") or "").strip().lower() == site
		and (r.get("note_type") or "") == "access_delay"
	]


def score_candidates(job: Job, eligible: list[tuple[Technician, float]], records: list[dict]) -> list[dict]:
	"""
	Score each eligible (tech, distance_miles) pair.

	base_score mirrors the base router's behaviour (distance only) on a
	0-100 scale; memory modifiers are added on top with full evidence.
	"""
	access_notes = _site_access_notes(job, records)
	candidates = []
	for rank, (tech, distance_miles) in enumerate(
		sorted(eligible, key=lambda pair: pair[1]), start=1
	):
		distance_km = round(distance_miles * MILES_TO_KM, 1)
		base_score = round(max(0.0, 100.0 - distance_km * 6.0), 1)
		stats = _tech_stats(tech, job, records)

		modifiers = []
		if stats["similar_area_success"] >= 1:
			modifiers.append({
				"label": f"{stats['similar_area_success']} successful similar {job_category(job)} job(s) in {route_area_name(job.route_criteria)}",
				"points": MOD_SIMILAR_AREA_SUCCESS,
				"evidence": stats["evidence"]["similar_area_success"],
			})
		if stats["site_success"] >= 1:
			modifiers.append({
				"label": f"Successful history at {job.customer_name} ({stats['site_success']} job(s))",
				"points": MOD_SITE_SUCCESS,
				"evidence": [],
			})
		if stats["skill_success"] >= 1:
			modifiers.append({
				"label": f"Skill-specific success on {job_category(job)} ({stats['skill_success']} job(s))",
				"points": MOD_SKILL_SUCCESS,
				"evidence": [],
			})
		if stats["overruns"] >= 2:
			modifiers.append({
				"label": f"Repeated overruns on {job_category(job)} ({stats['overruns']} recalled)",
				"points": MOD_REPEAT_OVERRUNS,
				"evidence": stats["evidence"]["overruns"],
			})
		if stats["complaints"] >= 1:
			modifiers.append({
				"label": f"Previous poor customer rating at {job.customer_name}",
				"points": MOD_CUSTOMER_COMPLAINT,
				"evidence": stats["evidence"]["complaints"],
			})
		if stats["temporary_fixes"] >= 1:
			modifiers.append({
				"label": "Previous fix was temporary / issue reopened",
				"points": MOD_TEMPORARY_FIX,
				"evidence": stats["evidence"]["temporary_fixes"],
			})
		if stats["total_memories"] == 0 and job.priority == 1:
			modifiers.append({
				"label": "No memory of this technician — unproven on a VIP emergency",
				"points": MOD_UNKNOWN_ON_VIP,
				"evidence": [],
			})
		if access_notes and stats["site_visits"] == 0:
			modifiers.append({
				"label": f"{job.customer_name} has access-delay history and this tech has no site familiarity",
				"points": MOD_ACCESS_RISK,
				"evidence": [n.get("raw", "")[:220] for n in access_notes[:2]],
			})

		memory_points = sum(m["points"] for m in modifiers)
		negative_points = sum(m["points"] for m in modifiers if m["points"] < 0)
		risk_level = "high" if negative_points <= -40 else ("medium" if negative_points < 0 else "low")

		candidates.append({
			"technician_id": tech.id,
			"technician_name": tech.name,
			"employee_id": tech.employee_id,
			"skills": tech.skills,
			"distance_km": distance_km,
			"base_rank": rank,
			"base_score": base_score,
			"memory_modifiers": modifiers,
			"memory_points": memory_points,
			"memory_score": round(base_score + memory_points, 1),
			"memory_risk": risk_level,
			"stats": {k: v for k, v in stats.items() if k != "evidence"},
			"site_familiarity": "high" if stats["site_visits"] >= 2 else ("medium" if stats["site_visits"] == 1 else "low"),
		})
	return candidates


def _suggested_note(job: Job, records: list[dict]) -> Optional[str]:
	notes = _site_access_notes(job, records)
	for n in notes:
		action = n.get("suggested_action")
		if action and "call" in action.lower():
			return action
	if notes:
		return notes[0].get("suggested_action") or notes[0].get("details")
	return None


def build_explanation(job: Job, candidates: list[dict], records: list[dict]) -> str:
	category = job_category(job)
	area = route_area_name(job.route_criteria)
	site = job.customer_name
	event_records = [r for r in records if r.get("record_type") == "FIELD_JOB_EVENT"]
	similar = [
		r for r in event_records
		if _is_category_match(r, category)
		and (r.get("route_area") or "").strip().lower() == area.strip().lower()
	]
	site_events = [r for r in event_records if (r.get("site") or "").strip().lower() == site.lower()]
	access = _site_access_notes(job, records)

	base = min(candidates, key=lambda c: c["base_rank"]) if candidates else None
	best = max(candidates, key=lambda c: c["memory_score"]) if candidates else None
	if not base or not best:
		return "No eligible technicians found for this job."

	parts = []
	if len(similar) >= 2 or len(site_events) >= 2:
		parts.append(
			f"This is probably not an isolated {category} ticket. Cognee recalls "
			f"{len(similar)} similar {area} {category} incident(s)"
			+ (f" and {len(access)} previous {site} access delay(s)." if access else ".")
		)
	if base["technician_id"] != best["technician_id"]:
		neg = [m["label"] for m in base["memory_modifiers"] if m["points"] < 0]
		parts.append(
			f"Closest technician is {base['technician_name']} ({base['distance_km']} km), "
			f"but memory flags: {'; '.join(neg) if neg else 'lower recalled reliability on this job type'}."
		)
		pos = [m["label"] for m in best["memory_modifiers"] if m["points"] > 0]
		parts.append(
			f"Recommended technician: {best['technician_name']} ({best['distance_km']} km) — "
			f"{'; '.join(pos) if pos else 'stronger recalled track record'}."
		)
	else:
		parts.append(
			f"Memory confirms the base router: {best['technician_name']} is both closest "
			f"and has the strongest recalled track record for this job."
		)
	return " ".join(parts)


async def get_eligible_with_distance(db: AsyncSession, job: Job) -> list[tuple[Technician, float]]:
	"""
	Same eligibility rules as the base router (skill + route + time).
	Also includes the job's currently-assigned technician (if any) so
	re-running the routers on an assigned job still shows the comparison.
	"""
	available = list(await tech_logic.get_available_technicians(db))
	if job.assignment:
		assigned_tech = await tech_logic.get_technician(db, job.assignment.technician_id)
		if assigned_tech and all(t.id != assigned_tech.id for t in available):
			available.append(assigned_tech)
	eligible = []
	for tech in available:
		result = job_logic.can_technician_do_job(job, tech)
		if not result["can_do"]:
			continue
		origin_lat = tech.current_latitude if tech.current_latitude is not None else tech.home_latitude
		origin_lon = tech.current_longitude if tech.current_longitude is not None else tech.home_longitude
		distance = haversine_distance(origin_lat, origin_lon, job.latitude, job.longitude)
		eligible.append((tech, distance))
	return eligible


async def memory_aware_route(db: AsyncSession, job_id: int, recall: Optional[dict] = None) -> dict:
	"""
	Run both routers for a job:
	  1. base router recommendation (closest qualified — existing logic)
	  2. memory-aware recommendation (base score + Cognee recall modifiers)

	Pass a pre-fetched `recall` (from cognee_memory.recall_job_context) to
	avoid a second identical cloud round-trip when the caller already has one.
	Raises CogneeNotConfigured when the memory layer is unavailable.
	"""
	job = await job_logic.get_job(db, job_id)
	if not job:
		raise ValueError(f"Job {job_id} not found")

	eligible = await get_eligible_with_distance(db, job)
	if not eligible:
		return {
			"job_id": job_id,
			"has_match": False,
			"message": "No eligible technicians for this job (skill/route/time).",
		}

	# REAL Cognee recall — raises CogneeNotConfigured if the layer is off
	if recall is None:
		recall = await cognee_memory.recall_job_context(job)
	records = recall["records"]

	candidates = score_candidates(job, eligible, records)
	base = min(candidates, key=lambda c: c["base_rank"])
	best = max(candidates, key=lambda c: c["memory_score"])

	relevant = sum(c["stats"]["total_memories"] for c in candidates)
	confidence = round(min(0.95, 0.45 + 0.05 * relevant + 0.02 * len(records)), 2)

	return {
		"job_id": job.id,
		"job_number": job.job_number,
		"customer_name": job.customer_name,
		"route_area": route_area_name(job.route_criteria),
		"job_category": job_category(job),
		"has_match": True,
		"routing_mode": "memory_aware",
		"base_router_technician": {
			"technician_id": base["technician_id"],
			"technician_name": base["technician_name"],
			"distance_km": base["distance_km"],
		},
		"recommended_technician": {
			"technician_id": best["technician_id"],
			"technician_name": best["technician_name"],
			"distance_km": best["distance_km"],
		},
		"recommendation_changed": base["technician_id"] != best["technician_id"],
		"confidence_score": confidence,
		"risk_level": base["memory_risk"] if base["technician_id"] != best["technician_id"] else best["memory_risk"],
		"explanation": build_explanation(job, candidates, records),
		"suggested_dispatch_note": _suggested_note(job, records),
		"scoring_breakdown": candidates,
		"recalled_memories": recall["chunks"][:20],
		"recall_query": recall["query"],
		"memories_recalled": len(records),
	}
