"""
Duration sampler — estimates actual on-site duration for a (job, tech) pair.

Seeded log-normal on (job_id, tech_id): deterministic per pair, so repeated
assignment of the same job to the same technician predicts the same duration.

final_multiplier = tech.speed_factor * tech.skill_bonuses.get(job_type, 1.0)
mean_duration    = job.estimated_duration * final_multiplier
"""
import numpy as np

from backend.database.models import Job, Technician

_SIGMA = 0.25  # log-normal spread — moderate real-world variability


def _seed(job_id: int, tech_id: int) -> int:
	return abs(hash((job_id, tech_id))) % (2 ** 32)


def sample_duration(job: Job, tech: Technician) -> int:
	"""Sample actual duration (minutes); stored on Assignment at assign time."""
	rng = np.random.default_rng(seed=_seed(job.id, tech.id))
	multiplier = tech.speed_factor * tech.skill_bonuses.get(job.job_type.value, 1.0)
	mean = job.estimated_duration * multiplier
	mu = np.log(mean) - (_SIGMA ** 2) / 2
	minutes = int(round(float(rng.lognormal(mu, _SIGMA))))
	return max(1, minutes)
