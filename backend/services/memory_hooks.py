"""
Smriti — automatic lifecycle memory hooks.

Part of the Smriti Cognee memory layer.

Job lifecycle events (created / assigned / reassigned / started /
completed / cancelled / override) are remembered into Cognee in the
background so dispatch API calls stay fast. Each hook opens its own DB
session (the request session is gone by the time the task runs).

If Cognee is not configured the hook is a no-op beyond the local audit
row marking the event as skipped — the base dispatch flow never breaks.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from backend.database.connection import AsyncSessionLocal
from backend.services import cognee_memory

logger = logging.getLogger(__name__)


async def _remember_job_event_task(
	event_type: str,
	job_id: int,
	notes: Optional[str] = None,
	outcome: Optional[dict] = None,
	improve: bool = False,
):
	try:
		async with AsyncSessionLocal() as session:
			from backend.logic import jobs as job_logic
			job = await job_logic.get_job(session, job_id)
			if not job:
				return
			technician = job.assignment.technician if job.assignment else None
			if improve:
				await cognee_memory.improve_after_job_completion(
					session, job, technician, outcome or {"result": "resolved"},
				)
			else:
				await cognee_memory.remember_job_event(
					session, event_type, job, technician, job.assignment,
					outcome=outcome, notes=notes,
				)
	except cognee_memory.CogneeNotConfigured:
		pass  # audit row already records skipped_not_configured
	except Exception:  # noqa: BLE001 — memory failures must never break dispatch
		logger.exception("Background %s memory hook failed for job %s", event_type, job_id)


def remember_event(
	event_type: str,
	job_id: int,
	notes: Optional[str] = None,
	outcome: Optional[dict] = None,
	improve: bool = False,
):
	"""Schedule a fire-and-forget lifecycle memory write."""
	asyncio.create_task(
		_remember_job_event_task(event_type, job_id, notes=notes, outcome=outcome, improve=improve)
	)
