import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

/**
 * MemoryPanel — the Cognee Memory Insight panel (Smriti layer).
 *
 * Docked right-side panel showing, for the active job:
 *   - repeat-issue detection, badges, risk levels
 *   - technician comparison (base router vs memory-aware)
 *   - full scoring breakdown (why the recommendation changed)
 *   - suggested dispatcher note + recalled memory snippets
 *   - forget-customer privacy action
 *
 * All content comes from real Cognee recall via /api/v1/memory endpoints.
 * If Cognee is not configured, shows the backend's configuration error.
 */
export default function MemoryPanel({ job, onClose, onAssignTech, onInsight, toast, refreshKey }) {
	const [insight, setInsight] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const [showMemories, setShowMemories] = useState(false);
	const [forgetting, setForgetting] = useState(false);
	const [confirmForget, setConfirmForget] = useState(false);
	const [forgetResult, setForgetResult] = useState(null);
	const [activity, setActivity] = useState([]);

	// The learning feed — what Smriti recently remembered / improved /
	// forgot. Makes the memory lifecycle observable, not implicit.
	useEffect(() => {
		let alive = true;
		const loadActivity = () =>
			api.memoryEvents(12)
				.then((r) => { if (alive) setActivity(r.data); })
				.catch(() => {});
		loadActivity();
		const i = setInterval(loadActivity, 15000);
		return () => { alive = false; clearInterval(i); };
	}, [refreshKey, job?.id]);

	const load = useCallback(async () => {
		if (!job) return;
		setLoading(true);
		setError(null);
		setForgetResult(null);
		try {
			const res = await api.jobInsights(job.id);
			setInsight(res.data);
			onInsight?.(job.id, res.data);
		} catch (e) {
			setError(e.response?.data?.detail || 'Failed to recall memory for this job.');
			setInsight(null);
		} finally {
			setLoading(false);
		}
	}, [job?.id, refreshKey]); // eslint-disable-line

	useEffect(() => { load(); }, [load]);

	const handleForget = async () => {
		setForgetting(true);
		try {
			const res = await api.forgetCustomer(job.customer_name);
			setForgetResult(res.data.message);
			setConfirmForget(false);
			toast?.('Cognee forget completed', 'success');
		} catch (e) {
			toast?.(e.response?.data?.detail || 'Forget failed', 'error');
		} finally {
			setForgetting(false);
		}
	};

	if (!job) return null;

	const base = insight?.base_router_technician;
	const rec = insight?.recommended_technician;
	const changed = insight?.recommendation_changed;
	const candidates = insight?.technician_insights || [];
	const sorted = [...candidates].sort((a, b) => b.memory_score - a.memory_score);

	return (
		<div className="memory-panel">
			<div className="mp-header">
				<span className="mp-title"><BrainIcon /> Cognee Memory Insight</span>
				<button className="mp-close" onClick={onClose}>✕</button>
			</div>
			<div className="mp-job-line">
				<span className="mp-job-number">#{job.job_number || job.id}</span>
				<span className="mp-job-cust">{job.customer_name}</span>
				{insight && <span className="mp-job-cat">{insight.job_category} · {insight.route_area}</span>}
			</div>

			<div className="mp-body">
				{loading && (
					<div className="mp-loading">
						<div className="loading-spinner" />
						Recalling from Cognee Cloud…
					</div>
				)}

				{error && !loading && (
					<div className="mp-error">
						<div className="mp-error-title">Memory layer unavailable</div>
						<div className="mp-error-text">{error}</div>
						<button className="btn btn--sm" onClick={load}>Retry</button>
					</div>
				)}

				{insight && !loading && (
					<>
						{/* Badges */}
						{insight.badges?.length > 0 && (
							<div className="mp-badges">
								{insight.badges.map((b) => (
									<span key={b.key} className={`mp-badge mp-badge--${b.key}`} title={b.detail}>
										{b.label}
									</span>
								))}
							</div>
						)}

						{/* Repeat issue */}
						<div className="mp-section">
							<div className="mp-section-title">Is this a repeat issue?</div>
							<div className={`mp-repeat ${insight.is_repeat_issue ? 'mp-repeat--yes' : ''}`}>
								{insight.is_repeat_issue ? '⚠ Yes — ' : 'No clear repeat pattern. '}
								{insight.repeat_summary}
							</div>
						</div>

						{/* Explanation */}
						<div className="mp-section">
							<div className="mp-section-title">Why memory {changed ? 'changed' : 'confirmed'} the route</div>
							<div className="mp-explanation">{insight.explanation}</div>
							<div className="mp-meta-row">
								<span className={`mp-risk mp-risk--${insight.risk_level}`}>risk: {insight.risk_level}</span>
								<span className="mp-confidence">confidence {Math.round((insight.confidence_score || 0) * 100)}%</span>
								<span className="mp-mem-count">{insight.memories_recalled} memories recalled</span>
							</div>
						</div>

						{/* Verdict */}
						{base && rec && (
							<div className={`mp-verdict ${changed ? 'mp-verdict--changed' : ''}`}>
								{changed ? (
									<>Base router would choose <strong>{base.technician_name}</strong>.
										{' '}Smriti recommends <strong>{rec.technician_name}</strong>.</>
								) : (
									<>Base router and memory agree: <strong>{rec.technician_name}</strong>.</>
								)}
							</div>
						)}

						{/* Technician comparison cards */}
						<div className="mp-section">
							<div className="mp-section-title">Technician comparison</div>
							<div className="mp-tech-cards">
								{sorted.map((c) => {
									const isRec = rec && c.technician_id === rec.technician_id;
									const isBase = base && c.technician_id === base.technician_id;
									return (
										<div key={c.technician_id} className={`mp-tech-card${isRec ? ' mp-tech-card--rec' : ''}`}>
											<div className="mp-tech-head">
												<span className="mp-tech-name">{c.technician_name}</span>
												{isRec && <span className="mp-badge mp-badge--recommended_by_memory">Recommended by Memory</span>}
												{isBase && !isRec && <span className="mp-badge mp-badge--base">Base #1</span>}
											</div>
											<div className="mp-tech-stats">
												<span>Distance: <strong>{c.distance_km} km</strong></span>
												<span>Base rank: <strong>#{c.base_rank}</strong></span>
												<span>Memory risk: <strong className={`mp-risk-text--${c.memory_risk}`}>{c.memory_risk}</strong></span>
												<span>Similar wins: <strong>{c.stats.similar_area_success}</strong></span>
												<span>Overruns: <strong>{c.stats.overruns}</strong></span>
												<span>Site familiarity: <strong>{c.site_familiarity}</strong></span>
											</div>
											<div className="mp-score-line">
												<span>base {c.base_score}</span>
												<span className={c.memory_points >= 0 ? 'mp-pts-pos' : 'mp-pts-neg'}>
													{c.memory_points >= 0 ? '+' : ''}{c.memory_points} memory
												</span>
												<span className="mp-score-final">= {c.memory_score}</span>
											</div>
											{c.memory_modifiers.length > 0 && (
												<ul className="mp-modifiers">
													{c.memory_modifiers.map((m, i) => (
														<li key={i} className={m.points >= 0 ? 'mp-mod-pos' : 'mp-mod-neg'}>
															<span className="mp-mod-pts">{m.points > 0 ? '+' : ''}{m.points}</span> {m.label}
														</li>
													))}
												</ul>
											)}
											{onAssignTech && job.status === 'pending' && (
												<button
													className={`btn btn--sm ${isRec ? 'btn--primary' : ''}`}
													onClick={() => onAssignTech(c.technician_id, insight)}
												>
													Assign {c.technician_name.split(' ')[0]}
												</button>
											)}
										</div>
									);
								})}
								{sorted.length === 0 && <div className="mp-muted">No eligible technicians.</div>}
							</div>
						</div>

						{/* Suggested dispatch note */}
						{insight.suggested_dispatch_note && (
							<div className="mp-section">
								<div className="mp-section-title">Suggested dispatcher note</div>
								<div className="mp-dispatch-note">📞 {insight.suggested_dispatch_note}</div>
							</div>
						)}

						{/* Site history */}
						{insight.site_history?.length > 0 && (
							<div className="mp-section">
								<div className="mp-section-title">Site history — {job.customer_name}</div>
								<ul className="mp-history">
									{insight.site_history.slice(0, 5).map((r, i) => (
										<li key={i}>
											<span className="mp-hist-date">{r.date || ''}</span>{' '}
											<span className="mp-hist-tech">{r.technician}</span> — {r.job_type},{' '}
											<span className={r.reopened === 'yes' ? 'mp-mod-neg' : 'mp-mod-pos'}>{r.result || r.outcome}</span>
											{r.customer_rating && <> · ★{r.customer_rating}</>}
										</li>
									))}
								</ul>
							</div>
						)}

						{/* Recalled memory snippets */}
						<div className="mp-section">
							<button className="mp-toggle" onClick={() => setShowMemories((p) => !p)}>
								{showMemories ? '▾' : '▸'} Recalled memory snippets ({insight.recalled_memories?.length || 0})
							</button>
							{showMemories && (
								<div className="mp-memories">
									{(insight.recalled_memories || []).map((m, i) => (
										<pre key={i} className="mp-memory-snippet">{m.slice(0, 420)}</pre>
									))}
								</div>
							)}
						</div>

						{/* Memory activity — the observable learning loop */}
						<div className="mp-section">
							<div className="mp-section-title">Memory activity — what Smriti learned recently</div>
							{activity.length === 0 ? (
								<div className="mp-muted">No memory operations yet this session.</div>
							) : (
								<ul className="mp-activity">
									{activity.map((e) => (
										<li key={e.id} className={`mp-act mp-act--${e.cognee_status}`}>
											<span className="mp-act-icon">{ACT_ICON[e.event_type] || '•'}</span>
											<span className="mp-act-text">
												<strong>{(e.event_type || '').replace(/_/g, ' ')}</strong>
												{e.site_name ? <> — {e.site_name}</> : null}
												{e.route_area ? <> · {e.route_area}</> : null}
											</span>
											<span className={`mp-act-status mp-act-status--${e.cognee_status}`}>
												{e.cognee_status === 'ok' ? 'learned' : e.cognee_status === 'error' ? 'failed' : 'skipped'}
											</span>
										</li>
									))}
								</ul>
							)}
							<div className="mp-loop-hint">
								Complete a job (right-click → Complete) and reopen this panel — the
								outcome is remembered + improved, and the technician's stats above
								change on the next recall.
							</div>
						</div>

						{/* Right to be forgotten (DPDP / GDPR) */}
						<div className="mp-section mp-forget">
							<div className="mp-section-title">Right to be forgotten (DPDP / GDPR)</div>
							<div className="mp-forget-explain">
								For customer offboarding or a legal erasure request — not everyday use.
								Deletes <strong>{job.customer_name}</strong>'s identifiable site memory;
								anonymized operational patterns (technician outcomes by job type and
								area) are retained, so routing intelligence survives.
							</div>
							{forgetResult ? (
								<div className="mp-forget-result">✅ {forgetResult}</div>
							) : confirmForget ? (
								<div className="mp-forget-confirm">
									<div>Erase all Cognee memory identifying <strong>{job.customer_name}</strong>?</div>
									<div className="mp-forget-actions">
										<button className="btn btn--sm" onClick={() => setConfirmForget(false)}>Cancel</button>
										<button className="btn btn--sm btn--danger" onClick={handleForget} disabled={forgetting}>
											{forgetting ? 'Erasing…' : 'Yes, erase'}
										</button>
									</div>
								</div>
							) : (
								<button className="btn btn--sm" onClick={() => setConfirmForget(true)}>
									🗑 Erase this customer's memory
								</button>
							)}
						</div>
					</>
				)}
			</div>
		</div>
	);
}

const ACT_ICON = {
	job_created: '📋',
	job_assigned: '👷',
	job_reassigned: '🔁',
	job_started: '▶️',
	job_completed: '✅',
	job_cancelled: '✖️',
	dispatch_override: '⚠️',
	improve: '📈',
	forget_customer: '🗑',
	memory_seed_india: '🌱',
};

function BrainIcon() {
	return (
		<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.3">
			<path d="M6 2.5a2 2 0 00-2 2c-1 .3-1.7 1.2-1.7 2.3 0 .6.2 1.1.5 1.5-.3.4-.5.9-.5 1.5 0 1.2 1 2.2 2.2 2.2H6M6 2.5c.8 0 1.5.7 1.5 1.5v8c0 .8-.7 1.5-1.5 1.5M6 2.5v11M10 2.5a2 2 0 012 2c1 .3 1.7 1.2 1.7 2.3 0 .6-.2 1.1-.5 1.5.3.4.5.9.5 1.5 0 1.2-1 2.2-2.2 2.2H10M10 2.5c-.8 0-1.5.7-1.5 1.5v8c0 .8.7 1.5 1.5 1.5M10 2.5v11" />
		</svg>
	);
}
