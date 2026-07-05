"""
Smriti — Cognee Cloud memory service.

This is the Smriti Cognee memory layer.

All operational memory lives in Cognee (via the official `cognee` Python
SDK). This module wraps the four real memory verbs:

	cognee.remember(...)  — store a structured job event (add + cognify)
	cognee.recall(...)    — retrieve relevant memories for scoring/insights
	cognee.improve(...)   — consolidate/enrich the graph after completions
	cognee.forget(...)    — delete a customer's dataset (privacy demo)

Connection: `cognee.serve(url=COGNEE_CLOUD_URL, api_key=COGNEE_API_KEY)`
routes every operation to Cognee Cloud. There is NO fake fallback — if
Cognee is not configured, every function raises CogneeNotConfigured and
the memory API returns a clear configuration error while dispatch keeps
working.

Dataset layout (enables the privacy story):
	crewmind_ops_patterns       — anonymized operational patterns
	                              (site names redacted; job type, route
	                              area, technician, outcome kept)
	crewmind_customer_<slug>    — customer/site-specific memories.
	                              `forget_customer_memory` deletes this
	                              dataset; the anonymized ops dataset
	                              survives.

A local MemoryEvent audit row is written for every remember/improve/
forget call — for demo transparency only, never as a memory source.
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Any, Optional

from backend.config import get_settings
from backend.database.models import Job, Technician, Assignment, MemoryEvent

settings = get_settings()

# ── Module state ─────────────────────────────────────────────────────────────
_initialized: bool = False
_init_error: Optional[str] = None
_last_success: Optional[dict] = None  # {"operation": ..., "at": iso, "detail": ...}

RECALL_TIMEOUT_S = 90
REMEMBER_TIMEOUT_S = 600


class CogneeNotConfigured(Exception):
	"""Raised when memory operations are attempted without Cognee configured."""


def _config_error_message() -> str:
	if not settings.COGNEE_ENABLED:
		return (
			"Cognee memory layer is disabled (COGNEE_ENABLED=false). "
			"Set COGNEE_ENABLED=true, COGNEE_API_KEY and COGNEE_CLOUD_URL in .env "
			"to enable memory-aware dispatch. The base dispatch app works without it."
		)
	if _init_error:
		return f"Cognee initialization failed: {_init_error}"
	return (
		"Cognee is enabled but not configured. Provide COGNEE_API_KEY (and "
		"COGNEE_CLOUD_URL for Cognee Cloud), or an LLM_API_KEY for local mode."
	)


# ── Category / display-name helpers ─────────────────────────────────────────

# Order matters: first matching skill wins as the job's category
SKILL_CATEGORY = [
	("hvac", "HVAC repair"),
	("fiber", "telecom fiber outage"),
	("network", "office network outage"),
	("pos", "POS terminal issue"),
	("atm", "ATM downtime"),
	("elevator", "elevator fault"),
	("ups", "power backup/UPS failure"),
	("cctv", "CCTV outage"),
	("pump", "water pump failure"),
	("solar", "solar inverter issue"),
	("cold_storage", "cold storage temperature alert"),
	("generator", "generator maintenance"),
	("electrical", "electrical fault"),
]

ROUTE_AREA_NAMES = {
	"NOIDA-62": "Noida Sector 62",
	"NOIDA-18": "Noida Sector 18",
	"GR-NOIDA": "Greater Noida",
	"GHAZIABAD": "Ghaziabad",
	"CP": "Connaught Place",
	"SAKET": "Saket",
	"DWARKA": "Dwarka",
	"ROHINI": "Rohini",
	"OKHLA": "Okhla Industrial Area",
	"GGN-CYBER": "Gurugram Cyber City",
	"GGN-SOHNA": "Sohna Road",
	"MANESAR": "Manesar",
	"FARIDABAD": "Faridabad Industrial Area",
}


def job_category(job: Job) -> str:
	"""Human job category (e.g. 'HVAC repair') from required skills."""
	skills = job.required_skills or []
	for skill, category in SKILL_CATEGORY:
		if skill in skills:
			return category
	return (job.job_type.value if job.job_type else "repair").replace("_", " ")


def route_area_name(route_criteria: Optional[str]) -> str:
	return ROUTE_AREA_NAMES.get(route_criteria or "", route_criteria or "unknown area")


def customer_slug(customer_name: str) -> str:
	return re.sub(r"[^a-z0-9]+", "_", customer_name.lower()).strip("_")


def customer_dataset(customer_name: str) -> str:
	return f"{settings.COGNEE_CUSTOMER_DATASET_PREFIX}{customer_slug(customer_name)}"


# ── Initialization ───────────────────────────────────────────────────────────

async def _resolve_service_url(cloud_url: str, api_key: Optional[str]) -> str:
	"""
	Resolve the tenant's Cognee service instance URL.

	Cognee Cloud has two hosts: the management API (api.aws.cognee.ai) and a
	per-tenant service instance that actually serves remember/recall/improve/
	forget. If `cloud_url` exposes /api/v1/tenants/current/service-url, use
	the discovered instance; otherwise assume `cloud_url` IS the instance.
	"""
	if not api_key:
		return cloud_url
	try:
		import aiohttp
		async with aiohttp.ClientSession(headers={"X-Api-Key": api_key}) as session:
			async with session.get(
				f"{cloud_url.rstrip('/')}/api/v1/tenants/current/service-url",
				timeout=aiohttp.ClientTimeout(total=20),
			) as resp:
				if resp.status == 200:
					data = await resp.json()
					service_url = data.get("service_url")
					if service_url:
						return service_url
	except Exception:  # noqa: BLE001 — fall back to the configured URL
		pass
	return cloud_url


async def init_cognee() -> dict:
	"""
	Connect the Cognee SDK to Cognee Cloud (or verify local mode).

	Called at app startup and lazily before the first memory operation.
	Never raises on startup — records the error for /memory/status instead.
	"""
	global _initialized, _init_error
	if _initialized:
		return {"initialized": True}
	if not settings.COGNEE_ENABLED:
		_init_error = None
		return {"initialized": False, "reason": _config_error_message()}

	try:
		import cognee  # imported lazily so the base app never needs it at import time

		if settings.COGNEE_CLOUD_URL:
			# Direct mode — routes remember/recall/improve/forget to Cognee Cloud.
			# If the configured URL is Cognee's management API (api.aws.cognee.ai),
			# discover the tenant's actual service instance URL first.
			service_url = await _resolve_service_url(settings.COGNEE_CLOUD_URL, settings.COGNEE_API_KEY)
			await cognee.serve(url=service_url, api_key=settings.COGNEE_API_KEY)
		elif settings.COGNEE_API_KEY:
			# Cloud mode without explicit URL — SDK discovers the tenant
			await cognee.serve(api_key=settings.COGNEE_API_KEY)
		else:
			# Local embedded mode — cognee runs in-process and needs an LLM key
			import os
			if not os.getenv("LLM_API_KEY"):
				raise CogneeNotConfigured(
					"COGNEE_ENABLED=true but neither COGNEE_API_KEY (cloud) nor "
					"LLM_API_KEY (local mode) is set."
				)
		_initialized = True
		_init_error = None
		return {"initialized": True}
	except Exception as e:  # noqa: BLE001 — surface any SDK/connection error verbatim
		_init_error = f"{type(e).__name__}: {e}"
		return {"initialized": False, "reason": _init_error}


async def _require_cognee():
	"""Ensure Cognee is configured + initialized, else raise CogneeNotConfigured."""
	if not settings.COGNEE_ENABLED:
		raise CogneeNotConfigured(_config_error_message())
	if not _initialized:
		result = await init_cognee()
		if not result.get("initialized"):
			raise CogneeNotConfigured(_config_error_message())
	import cognee
	return cognee


def _mark_success(operation: str, detail: str = ""):
	global _last_success
	_last_success = {
		"operation": operation,
		"at": datetime.now(timezone.utc).isoformat(),
		"detail": detail[:200],
	}


# ── Audit log helper ─────────────────────────────────────────────────────────

async def _audit(
	db,
	event_type: str,
	payload_preview: str,
	cognee_status: str,
	job: Optional[Job] = None,
	technician: Optional[Technician] = None,
	customer_name: Optional[str] = None,
	site_name: Optional[str] = None,
	route_area: Optional[str] = None,
):
	"""Write a MemoryEvent audit row (demo transparency, not memory truth)."""
	if db is None:
		return
	event = MemoryEvent(
		event_type=event_type,
		job_id=job.id if job else None,
		technician_id=technician.id if technician else None,
		customer_name=customer_name or (job.customer_name if job else None),
		site_name=site_name or (job.customer_name if job else None),
		route_area=route_area or (job.route_criteria if job else None),
		payload_preview=payload_preview[:2000],
		cognee_status=cognee_status,
	)
	db.add(event)
	await db.commit()


# ── Memory text builders ─────────────────────────────────────────────────────

def build_job_event_text(
	event_type: str,
	job: Job,
	technician: Optional[Technician] = None,
	assignment: Optional[Assignment] = None,
	outcome: Optional[dict] = None,
	notes: Optional[str] = None,
	anonymize: bool = False,
) -> str:
	"""
	Rich structured memory text + JSON metadata for a job lifecycle event.

	Anonymized variant (for the ops-patterns dataset) redacts customer/site
	identity but keeps the operational pattern.
	"""
	outcome = outcome or {}
	site = "[REDACTED SITE]" if anonymize else job.customer_name
	address = "[REDACTED]" if anonymize else f"{job.service_address}, {job.service_city or ''}".strip(", ")
	lines = [
		"FIELD_JOB_EVENT",
		f"event_type={event_type}",
		f"job_number={job.job_number or job.id}",
		f"job_type={job_category(job)}",
		f"base_job_type={job.job_type.value if job.job_type else 'repair'}",
		f"site={site}",
		f"address={address}",
		f"route_area={route_area_name(job.route_criteria)}",
		f"priority={'VIP/emergency' if job.priority == 1 else job.priority}",
		f"required_skills={','.join(job.required_skills or [])}",
	]
	if technician:
		lines.append(f"technician={technician.name}")
	if job.time_slot_start and job.time_slot_end:
		lines.append(f"scheduled_window={job.time_slot_start}-{job.time_slot_end}")
	if assignment is not None and assignment.estimated_distance is not None:
		lines.append(f"travel_distance_km={round(assignment.estimated_distance * 1.60934, 1)}")
	for key in (
		"actual_duration_minutes", "arrival_delay_minutes", "result", "customer_rating",
		"fix_type", "parts_used", "watch_recurrence", "overran", "reopened",
	):
		if outcome.get(key) is not None:
			lines.append(f"{key}={outcome[key]}")
	if job.description:
		lines.append(f"symptoms={job.description}")
	if notes:
		lines.append(f"notes={notes}")
	if outcome.get("lesson"):
		lines.append(f"lesson={outcome['lesson']}")

	metadata = {
		"kind": "field_job_event",
		"event_type": event_type,
		"job_id": job.id,
		"job_number": job.job_number,
		"job_category": job_category(job),
		"site": None if anonymize else job.customer_name,
		"route_area": route_area_name(job.route_criteria),
		"technician": technician.name if technician else None,
		"priority": job.priority,
		"synthetic_demo_data": True,
		"recorded_at": datetime.now(timezone.utc).isoformat(),
	}
	return "\n".join(lines) + "\nJSON_METADATA=" + json.dumps(metadata)


# ── Core operations (real Cognee calls) ──────────────────────────────────────

async def remember_job_event(
	db,
	event_type: str,
	job: Job,
	technician: Optional[Technician] = None,
	assignment: Optional[Assignment] = None,
	outcome: Optional[dict] = None,
	notes: Optional[str] = None,
) -> dict:
	"""
	Store a job lifecycle event in Cognee memory.

	Writes the full record to the customer's dataset and an anonymized
	record to the shared ops-patterns dataset, so `forget` can honor a
	customer while aggregate patterns survive.
	"""
	text_full = build_job_event_text(event_type, job, technician, assignment, outcome, notes, anonymize=False)
	try:
		cognee = await _require_cognee()
	except CogneeNotConfigured:
		await _audit(db, event_type, text_full, "skipped_not_configured", job, technician)
		raise

	text_anon = build_job_event_text(event_type, job, technician, assignment, outcome, notes, anonymize=True)
	try:
		await asyncio.wait_for(
			cognee.remember(text_full, dataset_name=customer_dataset(job.customer_name)),
			timeout=REMEMBER_TIMEOUT_S,
		)
		await asyncio.wait_for(
			cognee.remember(text_anon, dataset_name=settings.COGNEE_OPS_DATASET),
			timeout=REMEMBER_TIMEOUT_S,
		)
		_mark_success("remember", f"{event_type} job={job.job_number or job.id}")
		await _audit(db, event_type, text_full, "ok", job, technician)
		return {"remembered": True, "event_type": event_type, "datasets": [customer_dataset(job.customer_name), settings.COGNEE_OPS_DATASET]}
	except Exception as e:  # noqa: BLE001
		await _audit(db, event_type, f"{text_full}\n\nERROR: {e}", "error", job, technician)
		raise


async def remember_texts(db, texts_by_dataset: dict[str, list[str]], event_type: str = "memory_seed") -> dict:
	"""Bulk-remember pre-built memory texts, one remember() per dataset."""
	cognee = await _require_cognee()
	stored = {}
	for dataset, texts in texts_by_dataset.items():
		await asyncio.wait_for(
			cognee.remember(texts, dataset_name=dataset),
			timeout=REMEMBER_TIMEOUT_S,
		)
		stored[dataset] = len(texts)
	_mark_success("remember", f"{event_type}: {sum(stored.values())} records in {len(stored)} datasets")
	await _audit(
		db, event_type,
		json.dumps({ds: n for ds, n in stored.items()}),
		"ok",
	)
	return stored


def _entry_text(entry: Any) -> str:
	"""Normalize a cognee recall/search result entry to plain text."""
	if entry is None:
		return ""
	if isinstance(entry, str):
		return entry
	if isinstance(entry, dict):
		for key in ("text", "chunk", "content", "answer", "value", "payload", "context"):
			v = entry.get(key)
			if isinstance(v, str) and v.strip():
				return v
		return json.dumps(entry, default=str)
	for key in ("text", "chunk", "content", "answer", "value", "context"):
		v = getattr(entry, key, None)
		if isinstance(v, str) and v.strip():
			return v
	if hasattr(entry, "model_dump"):
		try:
			return json.dumps(entry.model_dump(), default=str)
		except Exception:  # noqa: BLE001
			pass
	return str(entry)


async def _recall_chunks(query: str, datasets: list[str], top_k: int = 40) -> list[str]:
	"""Run a real cognee.recall (CHUNKS retrieval) and normalize to text list."""
	cognee = await _require_cognee()
	from cognee import SearchType

	async def _run(ds: Optional[list[str]]):
		return await asyncio.wait_for(
			cognee.recall(query, query_type=SearchType.CHUNKS, datasets=ds, top_k=top_k),
			timeout=RECALL_TIMEOUT_S,
		)

	try:
		results = await _run(datasets)
	except Exception:
		# Datasets may not exist yet (e.g. no memories for this customer) —
		# retry across all datasets rather than failing the whole insight.
		results = await _run(None)
	_mark_success("recall", query[:120])
	texts = []
	for entry in results or []:
		t = _entry_text(entry)
		if t and t.strip():
			texts.append(t.strip())
	return texts


# ── Structured record parsing ────────────────────────────────────────────────

RECORD_HEADERS = ("FIELD_JOB_EVENT", "SITE_NOTE", "DISPATCH_OVERRIDE")


def parse_memory_records(texts: list[str]) -> list[dict]:
	"""
	Parse structured key=value records out of recalled memory chunks.

	Each seeded/remembered memory is one record: a header line followed by
	key=value lines. Chunks are split on header markers so a chunk holding
	multiple records still parses.
	"""
	parsed: list[dict] = []
	for text in texts:
		# Split the chunk wherever a new record header starts
		parts = re.split(r"(?=(?:" + "|".join(RECORD_HEADERS) + r")\b)", text)
		for part in parts:
			part = part.strip()
			header = next((h for h in RECORD_HEADERS if part.startswith(h)), None)
			if not header:
				continue
			record: dict[str, Any] = {"record_type": header, "raw": part[:1500]}
			for line in part.splitlines():
				m = re.match(r"^([a-z_]+)=(.*)$", line.strip())
				if m:
					record[m.group(1)] = m.group(2).strip()
			parsed.append(record)

	# Dedup: the same event exists as a full record (customer dataset) and an
	# anonymized copy (ops dataset, site redacted), and overlapping chunks can
	# repeat records. Key ignores the site so redacted/full copies collapse;
	# prefer the full (non-redacted) variant.
	def _key(r: dict):
		if r["record_type"] == "SITE_NOTE":
			# site is redacted in the ops copy — key on date + type + area
			return ("SITE_NOTE", r.get("date"), r.get("note_type"), r.get("route_area"))
		return (
			r["record_type"], r.get("event_type"), r.get("technician"),
			r.get("job_number") or r.get("date"),
			(r.get("symptoms") or "")[:60],
		)

	by_key: dict[tuple, dict] = {}
	for record in parsed:
		key = _key(record)
		existing = by_key.get(key)
		redacted = "[REDACTED" in (record.get("site") or "")
		if existing is None or ("[REDACTED" in (existing.get("site") or "") and not redacted):
			by_key[key] = record
	return list(by_key.values())


# ── Recall APIs used by insights + memory-aware routing ─────────────────────

async def recall_job_context(job: Job) -> dict:
	"""Recall memories relevant to a job: similar jobs, site history, tech history."""
	category = job_category(job)
	area = route_area_name(job.route_criteria)
	site = job.customer_name
	query = (
		f"{category} incidents, technician performance, overruns, access issues "
		f"at {site} and in {area}"
	)
	datasets = [settings.COGNEE_OPS_DATASET, customer_dataset(site)]
	texts = await _recall_chunks(query, datasets)
	records = parse_memory_records(texts)
	return {
		"query": query,
		"datasets": datasets,
		"chunks": texts,
		"records": records,
	}


async def recall_technician_context(job: Job, technician: Technician) -> dict:
	"""Recall memories about one technician for this job type/site/area."""
	category = job_category(job)
	area = route_area_name(job.route_criteria)
	query = (
		f"{technician.name} history with {category} jobs at {job.customer_name} "
		f"and in {area}: outcomes, durations, overruns, customer ratings"
	)
	datasets = [settings.COGNEE_OPS_DATASET, customer_dataset(job.customer_name)]
	texts = await _recall_chunks(query, datasets)
	records = [
		r for r in parse_memory_records(texts)
		if r.get("technician", "").lower() == technician.name.lower()
	]
	return {"query": query, "chunks": texts, "records": records}


async def recall_site_context(site_name: str, route_area: str, job_type: str) -> dict:
	"""Recall site/customer-specific memories (access issues, repeat problems)."""
	query = (
		f"{site_name} in {route_area}: {job_type} history, access delays, "
		f"security procedures, repeat issues, customer complaints"
	)
	datasets = [settings.COGNEE_OPS_DATASET, customer_dataset(site_name)]
	texts = await _recall_chunks(query, datasets)
	records = parse_memory_records(texts)
	site_records = [
		r for r in records
		if site_name.lower() in (r.get("site", "") or "").lower() or r.get("record_type") == "SITE_NOTE"
	]
	return {"query": query, "chunks": texts, "records": site_records or records}


async def improve_after_job_completion(db, job: Job, technician: Optional[Technician], outcome: dict) -> dict:
	"""
	Post-job learning: remember the completion outcome, then run
	cognee.improve() to consolidate the graph with the new evidence.
	"""
	remember_result = await remember_job_event(
		db, "job_completed", job, technician,
		assignment=job.assignment, outcome=outcome,
		notes=outcome.get("resolution_notes"),
	)
	cognee = await _require_cognee()
	improved = []
	for dataset in (customer_dataset(job.customer_name), settings.COGNEE_OPS_DATASET):
		try:
			await asyncio.wait_for(
				cognee.improve(dataset, run_in_background=True),
				timeout=REMEMBER_TIMEOUT_S,
			)
			improved.append(dataset)
		except Exception:  # noqa: BLE001
			# Some Cognee Cloud deployments don't expose /improve yet — the
			# closest real consolidation there is re-running the knowledge
			# graph pipeline over the dataset (cognify).
			try:
				await asyncio.wait_for(
					cognee.cognify(datasets=[dataset]),
					timeout=REMEMBER_TIMEOUT_S,
				)
				improved.append(f"{dataset} (via cognify)")
			except Exception as e2:  # noqa: BLE001 — enrichment only; remember already landed
				await _audit(db, "improve", f"dataset={dataset} ERROR: {e2}", "error", job, technician)
	if improved:
		_mark_success("improve", f"job={job.job_number or job.id}")
		await _audit(db, "improve", f"datasets={improved}", "ok", job, technician)
	return {**remember_result, "improved_datasets": improved}


async def forget_customer_memory(db, customer_name: str) -> dict:
	"""
	Privacy demo: forget everything Cognee knows about one customer/site.

	Deletes the customer's dedicated dataset via cognee.forget(dataset=...).
	The anonymized ops-patterns dataset (site names redacted) survives, so
	aggregate operational learning remains.
	"""
	cognee = await _require_cognee()
	dataset = customer_dataset(customer_name)
	try:
		result = await asyncio.wait_for(
			cognee.forget(dataset=dataset),
			timeout=REMEMBER_TIMEOUT_S,
		)
		_mark_success("forget", f"dataset={dataset}")
		await _audit(db, "forget_customer", f"dataset={dataset} result={result}", "ok",
		             customer_name=customer_name, site_name=customer_name)
		return {
			"forgotten": True,
			"customer": customer_name,
			"dataset": dataset,
			"cognee_result": str(result),
			"message": (
				f"Customer-specific memory for '{customer_name}' forgotten. "
				"Aggregated (anonymized) operational pattern memory remains."
			),
		}
	except Exception as e:  # noqa: BLE001
		await _audit(db, "forget_customer", f"dataset={dataset} ERROR: {e}", "error",
		             customer_name=customer_name, site_name=customer_name)
		raise


async def memory_healthcheck() -> dict:
	"""Report Cognee configuration/connection status + last successful op."""
	status = {
		"cognee_enabled": settings.COGNEE_ENABLED,
		"cognee_cloud_url": settings.COGNEE_CLOUD_URL,
		"api_key_present": bool(settings.COGNEE_API_KEY),
		"initialized": _initialized,
		"init_error": _init_error,
		"last_successful_operation": _last_success,
		"ops_dataset": settings.COGNEE_OPS_DATASET,
		"configured": False,
		"message": "",
	}
	if not settings.COGNEE_ENABLED:
		status["message"] = _config_error_message()
		return status
	init_result = await init_cognee()
	status["initialized"] = init_result.get("initialized", False)
	status["init_error"] = _init_error
	if status["initialized"]:
		status["configured"] = True
		status["message"] = "Cognee memory layer connected and ready."
	else:
		status["message"] = _config_error_message()
	return status
