import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { api } from '../api/client';
import TechGrid from './TechGrid';
import JobGrid from './JobGrid';
import ContextMenu from './ContextMenu';
import Toast from './Toast';
import JobDetailPanel from './JobDetailPanel';
import CalendarPicker from './CalendarPicker';
import MemoryPanel from './MemoryPanel';
import CompleteJobModal from './CompleteJobModal';
import OverrideReasonModal from './OverrideReasonModal';
import NewJobModal from './NewJobModal';
import NewTechModal from './NewTechModal';
import useToasts from '../hooks/useToasts';
import SmritiMark from './SmritiLogo';

/* ── Helpers ─────────────────────────────────────────────── */
function fmtDate(d) {
	return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
function fmtDateDisplay(d) {
	const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
	const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
	return `${days[d.getDay()]} ${months[d.getMonth()]} ${d.getDate()}`;
}
function sameDay(a, b) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }

export default function Dashboard({ onBrandClick }) {
	/* ── Data ─────────────────────────────────────────────── */
	const [techs, setTechs] = useState([]);
	const [jobs, setJobs] = useState([]);
	const [summary, setSummary] = useState(null);
	const [loading, setLoading] = useState(true);

	/* ── Day ──────────────────────────────────────────────── */
	const [viewDate, setViewDate] = useState(() => new Date());
	const [calOpen, setCalOpen] = useState(false);
	const calAnchorRef = useRef(null);
	const isToday = sameDay(viewDate, new Date());

	/* ── UI ───────────────────────────────────────────────── */
	const [splitRatio, setSplitRatio] = useState(0.4);
	const [dividerDrag, setDividerDrag] = useState(false);
	const [autoRouting, setAutoRouting] = useState(false);
	const [refreshing, setRefreshing] = useState(false);
	const splitRef = useRef(null);
	const [detailJob, setDetailJob] = useState(null);

	/* ── Override Warning (skill/route mismatch) ──────────── */
	const [overrideWarning, setOverrideWarning] = useState(null);
	// shape: { jobIds, techId, techName, issues: [{label, pass}] }

	/* ── Smriti — Cognee memory layer state ───────── */
	const [memoryJob, setMemoryJob] = useState(null);        // job shown in Memory Insight panel
	const [memoryConfigured, setMemoryConfigured] = useState(null); // null=unknown
	const [completeModalJob, setCompleteModalJob] = useState(null);
	const [memOverride, setMemOverride] = useState(null);
	// shape: { jobIds, techId, techName, recommendedId, recommendedName }
	const [newJobOpen, setNewJobOpen] = useState(false);
	const [newTechOpen, setNewTechOpen] = useState(false);
	const insightsRef = useRef({});                          // jobId -> last insight
	const [insightRefreshKey, setInsightRefreshKey] = useState(0);

	useEffect(() => {
		api.memoryStatus()
			.then((r) => setMemoryConfigured(!!r.data.configured))
			.catch(() => setMemoryConfigured(false));
	}, []);

	/* ── Autoroute confirmation ───────────────────────────── */
	const [autoRouteConfirm, setAutoRouteConfirm] = useState(false);

	/* ── Reset day confirmation ───────────────────────────── */
	const [resetConfirm, setResetConfirm] = useState(false);
	const [resetting, setResetting] = useState(false);

	/* ── Context menu ─────────────────────────────────────── */
	const [ctxMenu, setCtxMenu] = useState(null);

	/* ── Selection ────────────────────────────────────────── */
	const [selJobs, setSelJobs] = useState([]);
	const [selTechs, setSelTechs] = useState([]);

	/* ── Drag ─────────────────────────────────────────────── */
	const [dragJob, setDragJob] = useState(null);
	const techPaneRef = useRef(null);
	const techGridRef = useRef(null);
	const jobGridRef = useRef(null);
	const focusedGridRef = useRef('jobs'); // 'techs' | 'jobs'
	const dragJobRef = useRef(null);
	const dragGhostRef = useRef(null);
	const selJobsRef = useRef(selJobs);
	useEffect(() => { dragJobRef.current = dragJob; }, [dragJob]);
	useEffect(() => { selJobsRef.current = selJobs; }, [selJobs]);

	/* ── Real clock ───────────────────────────────────────── */
	const [realClock, setRealClock] = useState(() => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
	useEffect(() => {
		const i = setInterval(() => setRealClock(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })), 10000);
		return () => clearInterval(i);
	}, []);
	const techsRef = useRef([]);
	const fJobsRef = useRef([]);

	/* ── Filters (dashboard bar) ─────────────────────────── */
	const [jobFilter, setJobFilter] = useState(null);
	const [techFilter, setTechFilter] = useState(null);

	/* ── Toasts ───────────────────────────────────────────── */
	const [toasts, toast] = useToasts();

	/* ── Data loading ─────────────────────────────────────── */
	const loadData = useCallback(async (showRefresh = false) => {
		if (showRefresh) setRefreshing(true);
		const d = fmtDate(viewDate);
		try {
			const [tr, jr, sr] = await Promise.all([
				api.getTechnicians(),
				api.getJobs({ scheduled_date: d }),
				api.getJobsSummary({ target_date: d }),
			]);
			setTechs(tr.data);
			setJobs(jr.data);
			setSummary(sr.data);
		} catch (e) {
			console.error('Load error:', e);
			toast('Failed to load data', 'error');
		} finally {
			setLoading(false);
			setRefreshing(false);
		}
	}, [viewDate, toast]);

	useEffect(() => { setLoading(true); loadData(); }, [viewDate]); // eslint-disable-line
	useEffect(() => { const i = setInterval(() => loadData(), 30000); return () => clearInterval(i); }, [loadData]);
	useEffect(() => { techsRef.current = techs; }, [techs]);

	/* ── Close context menu ───────────────────────────────── */
	useEffect(() => { const c = () => setCtxMenu(null); document.addEventListener('click', c); return () => document.removeEventListener('click', c); }, []);

	/* ── Keyboard shortcuts ───────────────────────────────── */
	useEffect(() => {
		const h = (e) => {
			if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
			if (e.target.closest('.fw-window') || e.target.closest('.fw-job-detail')) return;
			if (e.key === 'Escape') { setCtxMenu(null); setDetailJob(null); }
			if (e.key === 'a' && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				if (focusedGridRef.current === 'techs') {
					setSelTechs((techsRef.current || []).map((t) => t.id));
					techGridRef.current?.selectAll();
				} else {
					setSelJobs((fJobsRef.current || []).map((j) => j.id));
					jobGridRef.current?.selectAll();
				}
				return;
			}
			if (e.key === 'r' && !e.ctrlKey && !e.metaKey) loadData(true);
			if (e.key === 'a' && !e.ctrlKey && !e.metaKey) setAutoRouteConfirm(true);
		};
		document.addEventListener('keydown', h);
		return () => document.removeEventListener('keydown', h);
	}, [loadData]);

	/* ── Day nav ──────────────────────────────────────────── */
	const goDay = useCallback((n) => setViewDate((p) => { const d = new Date(p); d.setDate(d.getDate() + n); return d; }), []);

	/* ── Drag system ─────────────────────────────────────── */
	useEffect(() => {
		if (!dragJob) return;
		const ghost = dragGhostRef.current;

		const updateGhost = (clientX, clientY) => {
			if (!ghost) return;
			const currentJob = dragJobRef.current;
			const currentSel = selJobsRef.current;
			ghost.style.left = `${clientX + 12}px`;
			ghost.style.top = `${clientY - 10}px`;
			ghost.style.display = 'block';
			ghost.textContent = currentSel.length > 1 && currentJob && currentSel.includes(currentJob.id)
				? `${currentSel.length} jobs`
				: currentJob ? `Job #${currentJob.job_number || currentJob.id} — ${currentJob.customer_name}` : '';
		};

		const dropAt = (clientX, clientY) => {
			const job = dragJobRef.current;
			if (job && techGridRef.current) {
				const pane = techPaneRef.current;
				const el = document.elementFromPoint(clientX, clientY);
				if (pane?.contains(el)) {
					const techId = techGridRef.current.getTechIdAtPoint(clientX, clientY);
					if (techId != null) {
						const currentSel = selJobsRef.current;
						const ids = currentSel.length > 0 && currentSel.includes(job.id) ? currentSel : [job.id];
						doAssignWithCheck(ids, techId);
					}
				}
			}
			if (ghost) ghost.style.display = 'none';
			setDragJob(null);
			document.body.style.userSelect = '';
			document.body.style.cursor = '';
		};

		const onMove = (e) => updateGhost(e.clientX, e.clientY);
		const onUp = (e) => dropAt(e.clientX, e.clientY);
		const onTouchMove = (e) => {
			e.preventDefault();
			const t = e.touches[0];
			updateGhost(t.clientX, t.clientY);
		};
		const onTouchEnd = (e) => {
			const t = e.changedTouches[0];
			dropAt(t.clientX, t.clientY);
		};

		document.addEventListener('mousemove', onMove);
		document.addEventListener('mouseup', onUp);
		document.addEventListener('touchmove', onTouchMove, { passive: false });
		document.addEventListener('touchend', onTouchEnd);
		return () => {
			document.removeEventListener('mousemove', onMove);
			document.removeEventListener('mouseup', onUp);
			document.removeEventListener('touchmove', onTouchMove);
			document.removeEventListener('touchend', onTouchEnd);
			if (ghost) ghost.style.display = 'none';
			document.body.style.userSelect = '';
			document.body.style.cursor = '';
		};
	}, [dragJob]); // eslint-disable-line

	/* ── Assign with CanDo + memory override check ────────── */
	const doAssignWithCheck = useCallback(async (jobIds, techId) => {
		const tech = techs.find((t) => t.id === techId);
		if (!tech) return;

		if (jobIds.length === 1) {
			const job = jobs.find((j) => j.id === jobIds[0]);
			if (job) {
				const issues = [];
				const missingSkills = (job.required_skills || []).filter((s) => !tech.skills?.includes(s));
				issues.push({ label: `Skill${missingSkills.length > 0 ? ` (missing: ${missingSkills.join(', ')})` : ''}`, pass: missingSkills.length === 0 });
				const routeMatch = !job.route_criteria || (tech.assigned_routes || []).includes(job.route_criteria);
				issues.push({ label: `Route${!routeMatch ? ` (job: ${job.route_criteria}, tech: ${(tech.assigned_routes || []).join(', ') || 'none'})` : ''}`, pass: routeMatch });

				const hasIssue = issues.some((i) => !i.pass);
				if (hasIssue) {
					setOverrideWarning({ jobIds, techId, techName: tech.name, issues });
					return;
				}

				// Smriti memory override check — if Cognee recommended a
				// different technician for this job, ask the dispatcher why.
				const insight = insightsRef.current[job.id];
				const rec = insight?.recommended_technician;
				if (rec && rec.technician_id !== techId && job.status === 'pending') {
					setMemOverride({
						jobIds, techId, techName: tech.name,
						recommendedId: rec.technician_id, recommendedName: rec.technician_name,
					});
					return;
				}
			}
		}

		await doBatchAssign(jobIds, techId);
	}, [techs, jobs]); // eslint-disable-line

	/* ── Batch assign (single API call) ───────────────────── */
	const doBatchAssign = useCallback(async (jobIds, techId) => {
		const tech = techs.find((t) => t.id === techId);
		if (!tech) return;
		try {
			const res = await api.batchAssign(jobIds, techId);
			const n = res.data.assigned ?? 0;
			toast(`${n} job${n !== 1 ? 's' : ''} → ${tech.name}`, n > 0 ? 'success' : 'warning');
			await loadData(true);
		} catch {
			toast('Assignment failed', 'error');
		}
	}, [techs, loadData, toast]);

	/* ── Override confirm (skill/route) ───────────────────── */
	const handleOverrideConfirm = useCallback(async () => {
		if (!overrideWarning) return;
		const { jobIds, techId } = overrideWarning;
		setOverrideWarning(null);
		await doBatchAssign(jobIds, techId);
	}, [overrideWarning, doBatchAssign]);

	/* ── Smriti memory override confirm ─────────────────── */
	const handleMemOverrideConfirm = useCallback(async (reason) => {
		if (!memOverride) return;
		const { jobIds, techId, recommendedId } = memOverride;
		setMemOverride(null);
		await doBatchAssign(jobIds, techId);
		// Remember the override in Cognee (best-effort — dispatch already done)
		try {
			await api.rememberOverride(jobIds[0], {
				assigned_technician_id: techId,
				recommended_technician_id: recommendedId,
				reason,
			});
			toast('Override remembered by Cognee', 'info');
		} catch {
			toast('Override stored locally (Cognee unavailable)', 'warning');
		}
	}, [memOverride, doBatchAssign, toast]);

	/* ── Smriti completion with learning ─────────────────── */
	const handleCompleteSubmit = useCallback(async (outcome) => {
		const job = completeModalJob;
		if (!job) return;
		setCompleteModalJob(null);
		try {
			if (job.status === 'assigned') await api.startJob(job.id).catch(() => {});
			await api.completeJobWithOutcome(job.id, outcome);
			toast(memoryConfigured ? '✅ Job completed — Cognee learned from this job' : `Job #${job.id} completed`, 'success');
			setInsightRefreshKey((k) => k + 1);
			await loadData(true);
		} catch (e) {
			toast(e.response?.data?.detail || 'Completion failed', 'error');
		}
	}, [completeModalJob, toast, loadData, memoryConfigured]);

	/* ── Batch unassign ───────────────────────────────────── */
	const doBatchUnassign = useCallback(async (jobIds) => {
		try {
			const res = await api.batchUnassign(jobIds);
			const n = res.data.unassigned ?? 0;
			toast(`${n} job${n !== 1 ? 's' : ''} unassigned`, n > 0 ? 'success' : 'warning');
			setSelJobs([]);
			await loadData(true);
		} catch {
			toast('Unassign failed', 'error');
		}
	}, [loadData, toast]);

	/* ── Reset day (reseeds dispatch data, keeps Cognee memory) ── */
	const handleResetDay = useCallback(async () => {
		setResetConfirm(false);
		setResetting(true);
		try {
			const res = await api.demoReset();
			setMemoryJob(null);
			insightsRef.current = {};
			setSelJobs([]); setSelTechs([]);
			toast(res.data.message, 'success');
			await loadData(true);
		} catch (e) {
			toast(e.response?.data?.detail || 'Reset failed', 'error');
		} finally {
			setResetting(false);
		}
	}, [toast, loadData]);

	/* ── Auto-route ───────────────────────────────────────── */
	const handleAutoRoute = useCallback(async () => {
		setAutoRouting(true);
		try {
			const res = await api.autoRoute({ target_date: fmtDate(viewDate) });
			const a = res.data.jobs_assigned ?? 0;
			const u = res.data.jobs_unassigned ?? 0;
			toast(`Routed ${a} job${a !== 1 ? 's' : ''}${u > 0 ? ` · ${u} unassigned` : ''}`, a > 0 ? 'success' : 'warning');
			await loadData(true);
		} catch { toast('Auto-route failed', 'error'); }
		finally { setAutoRouting(false); }
	}, [loadData, toast, viewDate]);

	/* ── Job actions ───────────────────────────────────────── */
	const handleJobAction = useCallback(async (action, job) => {
		setCtxMenu(null);
		const labels = { start: 'Started', complete: 'Completed', cancel: 'Cancelled', unassign: 'Unassigned', hold: 'On hold' };
		try {
			if (action === 'start') await api.startJob(job.id);
			else if (action === 'complete') { setCompleteModalJob(job); return; }
			else if (action === 'cancel') await api.cancelJob(job.id);
			else if (action === 'unassign') await api.unassignJob(job.id);
			else if (action === 'hold') await api.updateJobStatus(job.id, 'on_hold');
			else if (action === 'batch_unassign') { await doBatchUnassign(selJobs); return; }
			else return;
			toast(`Job #${job.id} — ${labels[action]}`, 'success');
			await loadData(true);
		} catch { toast(`Failed to ${action} job #${job.id}`, 'error'); }
	}, [loadData, toast, doBatchUnassign, selJobs]);

	/* ── Tech actions ──────────────────────────────────────── */
	const handleTechAction = useCallback(async (action, tech) => {
		setCtxMenu(null);
		const map = { set_available: 'available', set_on_break: 'on_break', set_off_duty: 'off_duty' };
		const status = map[action];
		if (!status) return;

		const techIds = selTechs.length > 1 && selTechs.includes(tech.id) ? selTechs : [tech.id];
		let successCount = 0;
		for (const tid of techIds) {
			try {
				await api.updateTechStatus(tid, status);
				successCount++;
			} catch (e) {
				console.error(`Failed to update tech ${tid}:`, e);
			}
		}
		if (successCount > 0) {
			const label = status.replace(/_/g, ' ');
			toast(
				techIds.length > 1
					? `${successCount} tech${successCount !== 1 ? 's' : ''} → ${label}`
					: `${tech.name} → ${label}`,
				'success'
			);
			await loadData(true);
		} else {
			toast('Failed to update status', 'error');
		}
	}, [loadData, toast, selTechs]);

	/* ── Context menu assign (with check) ────────────────── */
	const handleAssignToTech = useCallback(async (jobId, techId) => {
		setCtxMenu(null);
		const ids = selJobs.length > 0 && selJobs.includes(jobId) ? selJobs : [jobId];
		await doAssignWithCheck(ids, techId);
	}, [selJobs, doAssignWithCheck]);

	/* ── Selection (independent per grid) ─────────────────── */
	const handleJobClick = useCallback((id, e, displayedIds) => {
		setSelJobs((prev) => {
			if (e.metaKey || e.ctrlKey) return prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
			if (e.shiftKey && prev.length > 0 && displayedIds) {
				const lastSelected = prev[prev.length - 1];
				const a = displayedIds.indexOf(lastSelected);
				const b = displayedIds.indexOf(id);
				if (a === -1 || b === -1) return [id];
				const [start, end] = a < b ? [a, b] : [b, a];
				return [...new Set([...prev, ...displayedIds.slice(start, end + 1)])];
			}
			return prev.length === 1 && prev[0] === id ? [] : [id];
		});
	}, []);

	const handleTechClick = useCallback((id, e, displayedIds) => {
		setSelTechs((prev) => {
			if (e.metaKey || e.ctrlKey) return prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
			if (e.shiftKey && prev.length > 0 && displayedIds) {
				const lastSelected = prev[prev.length - 1];
				const a = displayedIds.indexOf(lastSelected);
				const b = displayedIds.indexOf(id);
				if (a === -1 || b === -1) return [id];
				const [start, end] = a < b ? [a, b] : [b, a];
				return [...new Set([...prev, ...displayedIds.slice(start, end + 1)])];
			}
			return prev.length === 1 && prev[0] === id ? [] : [id];
		});
	}, []);

	/* ── Double-click job for detail ─────────────────────── */
	const handleJobDoubleClick = useCallback((job) => {
		setDetailJob(job);
	}, []);

	/* ── Create job / technician ──────────────────────────── */
	const handleCreateJob = useCallback(async (payload) => {
		const res = await api.createJob(payload);
		setNewJobOpen(false);
		toast(`Job #${res.data.job_number || res.data.id} created — ${res.data.customer_name}`, 'success');
		await loadData(true);
		// New pending job → open its Memory Insight right away so the
		// dispatcher sees the recommendation as part of intake.
		setSelJobs([res.data.id]);
		setMemoryJob(res.data);
	}, [toast, loadData]);

	const handleCreateTech = useCallback(async (payload) => {
		const res = await api.createTechnician(payload);
		setNewTechOpen(false);
		toast(`Technician ${res.data.name} added`, 'success');
		await loadData(true);
	}, [toast, loadData]);

	/* ── Filter toggles (dashboard bar) ───────────────────── */
	const toggleJF = useCallback((s) => { setJobFilter((p) => p === s ? null : s); setTechFilter(null); }, []);
	const toggleTF = useCallback((s) => { setTechFilter((p) => p === s ? null : s); setJobFilter(null); }, []);

	/* ── Divider ─────────────────────────────────────────── */
	useEffect(() => {
		if (!dividerDrag) return;
		const onMove = (e) => {
			if (!splitRef.current) return;
			const r = splitRef.current.getBoundingClientRect();
			setSplitRatio(Math.min(Math.max((e.clientY - r.top) / r.height, 0.1), 0.85));
		};
		const onUp = () => setDividerDrag(false);
		document.addEventListener('mousemove', onMove);
		document.addEventListener('mouseup', onUp);
		document.body.style.cursor = 'row-resize';
		document.body.style.userSelect = 'none';
		return () => {
			document.removeEventListener('mousemove', onMove);
			document.removeEventListener('mouseup', onUp);
			document.body.style.cursor = '';
			document.body.style.userSelect = '';
		};
	}, [dividerDrag]);

	/* ── Computed: dashboard bar filters ─────────────────── */
	const active = useMemo(() => techs.filter((t) => ['available', 'on_job', 'en_route'].includes(t.status)).length, [techs]);
	const offDuty = useMemo(() => techs.filter((t) => t.status === 'off_duty').length, [techs]);

	const fJobs = useMemo(() => {
		return jobFilter ? jobs.filter((j) => j.status === jobFilter) : jobs;
	}, [jobs, jobFilter]);

	useEffect(() => { fJobsRef.current = fJobs; }, [fJobs]);

	const fTechs = useMemo(() => {
		if (techFilter === 'active') return techs.filter((t) => ['available', 'on_job', 'en_route'].includes(t.status));
		if (techFilter === 'off_duty') return techs.filter((t) => t.status === 'off_duty');
		return techs;
	}, [techs, techFilter]);

	/* ── Loading ──────────────────────────────────────────── */
	if (loading && techs.length === 0) return <div className="loading-screen"><div className="loading-spinner" />Loading Smriti...</div>;

	const s = summary ?? {};
	const pending = s.pending ?? 0, assigned = s.assigned ?? 0, inProg = s.in_progress ?? 0;
	const completed = s.completed ?? 0, onHold = s.on_hold ?? 0;

	return (
		<div className="app-shell">
			{/* ══ Header ══ */}
			<header className="header-bar">
				<button className="header-brand header-brand--link" title="Smriti home" onClick={() => onBrandClick?.()}>
					<div className="header-brand-icon header-brand-icon--smriti"><SmritiMark /></div>
					<span className="header-wordmark">Smriti</span>
				</button>
				<span className="header-real-clock">{realClock}</span>
				<div className="header-divider" />
				<div className="day-picker">
					<button className="day-picker-btn" onClick={() => goDay(-1)}>◂</button>
					<button
						ref={calAnchorRef}
						className={`day-picker-date${isToday ? ' day-picker-date--today' : ''}`}
						onClick={() => setCalOpen((p) => !p)}
					>
						{isToday ? 'Today' : fmtDateDisplay(viewDate)}
					</button>
					<button className="day-picker-btn" onClick={() => goDay(1)}>▸</button>
					{calOpen && (
						<CalendarPicker
							value={viewDate}
							onChange={(d) => setViewDate(d)}
							onClose={() => setCalOpen(false)}
							anchorRef={calAnchorRef}
						/>
					)}
				</div>
				<div className="header-actions">
					<button className="btn btn--primary" onClick={() => setNewJobOpen(true)}><PlusIcon /><span className="btn-label">New Job</span></button>
					<button className="btn" onClick={() => setNewTechOpen(true)}><PersonPlusIcon /><span className="btn-label">Add Technician</span></button>
					<div className="header-divider" />
					<button
						className={`btn${memoryJob ? ' btn--primary' : ''}`}
						title="Cognee Memory Insight for the selected job"
						onClick={() => {
							if (memoryJob) { setMemoryJob(null); return; }
							if (selJobs.length > 0) {
								const j = jobs.find((x) => x.id === selJobs[selJobs.length - 1]);
								if (j) { setMemoryJob(j); return; }
							}
							toast('Select a job first, then open Memory', 'warning');
						}}
					><BrainBtnIcon /><span className="btn-label">Memory</span></button>
					<button className="btn" onClick={() => loadData(true)} disabled={refreshing}><RefreshIcon spinning={refreshing} /><span className="btn-label">Refresh</span></button>
					<button className="btn" title="Reset the dispatch day (keeps Cognee memory)" onClick={() => setResetConfirm(true)} disabled={resetting}><ResetIcon spinning={resetting} /><span className="btn-label">{resetting ? 'Resetting…' : 'Reset Day'}</span></button>
					<button className="btn btn--warning" onClick={() => setAutoRouteConfirm(true)} disabled={autoRouting || pending === 0}>
						<BoltIcon /><span className="btn-label">{autoRouting ? 'Routing...' : `Auto-Route ${pending}`}</span>
					</button>
				</div>
			</header>

			{/* ══ Dashboard Bar ══ */}
			<div className="dashboard-bar">
				<DI active={jobFilter === 'pending'} onClick={() => toggleJF('pending')} count={pending} color="danger" label="Unassigned" />
				<DI active={jobFilter === 'assigned'} onClick={() => toggleJF('assigned')} count={assigned} color="info" label="Assigned" />
				<DI active={jobFilter === 'in_progress'} onClick={() => toggleJF('in_progress')} count={inProg} color="info" label="In Progress" />
				<DI active={jobFilter === 'completed'} onClick={() => toggleJF('completed')} count={completed} color="success" label="Completed" />
				<DI active={jobFilter === 'on_hold'} onClick={() => toggleJF('on_hold')} count={onHold} color="warning" label="On Hold" />
				<div className="header-divider" />
				<DI active={techFilter === 'active'} onClick={() => toggleTF('active')} count={active} color="success" label="Techs Active" />
				<DI active={techFilter === 'off_duty'} onClick={() => toggleTF('off_duty')} count={offDuty} color="muted" label="Off Duty" />
				<div className="dash-indicator"><span className="dash-count dash-count--muted">{techs.length}</span><span className="dash-label">Total</span></div>
				{(jobFilter || techFilter) && (
					<>
						<div className="header-divider" />
						<button className="dash-indicator dash-indicator--clear" onClick={() => { setJobFilter(null); setTechFilter(null); }}>
							✕ Clear
						</button>
					</>
				)}
			</div>

			{/* ══ Main row: split panes + Cognee Memory Insight panel ══ */}
			<div className="main-row">
			<div className="split-container" ref={splitRef}>
				{/* Tech pane */}
				<div className="pane" style={{ flex: `0 0 ${splitRatio * 100}%` }} onMouseDown={() => { focusedGridRef.current = 'techs'; }} onTouchStart={() => { focusedGridRef.current = 'techs'; }}>
					<div className="pane-header">
						<span className="pane-title">Technicians</span>
						<span className="pane-count">{fTechs.length}{techFilter ? ` / ${techs.length}` : ''}</span>
						{selTechs.length > 0 && <span className="pane-selection">{selTechs.length} selected</span>}
					</div>
					<div className="pane-body" ref={techPaneRef}>
						<TechGrid
							ref={techGridRef}
							technicians={fTechs}
							selectedIds={selTechs}
							onRowClicked={handleTechClick}
							onContextMenu={(e, t) => { e.preventDefault(); setCtxMenu({ x: e.clientX, y: e.clientY, type: 'tech', data: t }); }}
							isDragTarget={!!dragJob}
						/>
					</div>
				</div>

				<div className={`split-divider${dividerDrag ? ' split-divider--active' : ''}`} onMouseDown={(e) => { e.preventDefault(); setDividerDrag(true); }}>
					<div className="split-divider-grip" />
				</div>

				{/* Job pane */}
				<div className="pane" style={{ flex: 1 }} onMouseDown={() => { focusedGridRef.current = 'jobs'; }} onTouchStart={() => { focusedGridRef.current = 'jobs'; }}>
					<div className="pane-header">
						<span className="pane-title">Jobs</span>
						<span className="pane-count">{fJobs.length}{jobFilter ? ` / ${jobs.length}` : ''}</span>
						{selJobs.length > 0 && <span className="pane-selection">{selJobs.length} selected</span>}
					</div>
					<div className="pane-body">
						<JobGrid
							ref={jobGridRef}
							jobs={fJobs}
							selectedIds={selJobs}
							onRowClicked={handleJobClick}
							onContextMenu={(e, j) => { e.preventDefault(); setCtxMenu({ x: e.clientX, y: e.clientY, type: 'job', data: j }); }}
							onDragStart={(job) => { setDragJob(job); }}
							onRowDoubleClicked={handleJobDoubleClick}
						/>
					</div>
				</div>
			</div>

			{/* ══ Cognee Memory Insight panel (Smriti layer) ══ */}
			{memoryJob && (
				<MemoryPanel
					job={memoryJob}
					refreshKey={insightRefreshKey}
					onClose={() => setMemoryJob(null)}
					onInsight={(jobId, insight) => { insightsRef.current[jobId] = insight; }}
					onAssignTech={(techId) => doAssignWithCheck([memoryJob.id], techId)}
					toast={toast}
				/>
			)}
			</div>

			{/* ══ Drag Ghost — position written via ref to avoid re-renders ══ */}
			<div ref={dragGhostRef} className="drag-ghost" style={{ display: 'none' }} />

			{/* ══ Context Menu ══ */}
			{ctxMenu && (
				<ContextMenu
					x={ctxMenu.x} y={ctxMenu.y} type={ctxMenu.type} data={ctxMenu.data}
					technicians={techs}
					selectedJobIds={selJobs}
					selectedTechIds={selTechs}
					onJobAction={handleJobAction}
					onTechAction={handleTechAction}
					onAssignToTech={handleAssignToTech}
				/>
			)}

			{detailJob && (
				<JobDetailPanel
					job={detailJob}
					onClose={() => setDetailJob(null)}
				/>
			)}

			{/* ══ Autoroute Confirmation ══ */}
			{autoRouteConfirm && (
				<div className="override-overlay" onClick={() => setAutoRouteConfirm(false)}>
					<div className="override-modal" onClick={(e) => e.stopPropagation()}>
						<div className="override-title">Auto-Route Confirmation</div>
						<div className="override-body">
							Auto-route will assign <strong>{pending} pending job{pending !== 1 ? 's' : ''}</strong> to available technicians based on skill, route criteria, and distance.
						</div>
						<div className="override-actions">
							<button className="btn btn--sm" onClick={() => setAutoRouteConfirm(false)}>Cancel</button>
							<button className="btn btn--sm btn--warning" onClick={() => { setAutoRouteConfirm(false); handleAutoRoute(); }}>
								<BoltIcon />Route {pending} Jobs
							</button>
						</div>
					</div>
				</div>
			)}

			{/* ══ Reset Day Confirmation ══ */}
			{resetConfirm && (
				<div className="override-overlay" onClick={() => setResetConfirm(false)}>
					<div className="override-modal" onClick={(e) => e.stopPropagation()}>
						<div className="override-title">Reset the dispatch day?</div>
						<div className="override-body">
							Wipes and re-seeds today's technicians and jobs (fresh Delhi NCR day).
							<br /><strong>Cognee memory is kept</strong> — everything Smriti has learned survives the reset.
						</div>
						<div className="override-actions">
							<button className="btn btn--sm" onClick={() => setResetConfirm(false)}>Cancel</button>
							<button className="btn btn--sm btn--warning" onClick={handleResetDay}>↺ Reset Day</button>
						</div>
					</div>
				</div>
			)}

			{/* ══ Override Warning (skill/route) ══ */}
			{overrideWarning && (
				<div className="override-overlay" onClick={() => setOverrideWarning(null)}>
					<div className="override-modal" onClick={(e) => e.stopPropagation()}>
						<div className="override-title">Assignment Warning</div>
						<div className="override-body">
							Assigning {overrideWarning.jobIds.length === 1 ? `job #${overrideWarning.jobIds[0]}` : `${overrideWarning.jobIds.length} jobs`} to <strong>{overrideWarning.techName}</strong>:
							{overrideWarning.issues.map((issue, i) => (
								<div key={i} className="override-issue">
									<span className={issue.pass ? 'override-check' : 'override-x'}>
										{issue.pass ? '✓' : '✕'}
									</span>
									{issue.label}
								</div>
							))}
						</div>
						<div className="override-actions">
							<button className="btn btn--sm" onClick={() => setOverrideWarning(null)}>Cancel</button>
							<button className="btn btn--sm btn--warning" onClick={handleOverrideConfirm}>Assign Anyway</button>
						</div>
					</div>
				</div>
			)}

			{/* ══ New Job / Add Technician forms ══ */}
			{newJobOpen && (
				<NewJobModal
					onCancel={() => setNewJobOpen(false)}
					onSubmit={handleCreateJob}
					skillSuggestions={[...new Set(techs.flatMap((t) => t.skills || []))]}
				/>
			)}
			{newTechOpen && (
				<NewTechModal
					onCancel={() => setNewTechOpen(false)}
					onSubmit={handleCreateTech}
					skillSuggestions={[...new Set(techs.flatMap((t) => t.skills || []))]}
				/>
			)}

			{/* ══ Smriti memory override modal ══ */}
			{memOverride && (
				<OverrideReasonModal
					techName={memOverride.techName}
					recommendedName={memOverride.recommendedName}
					onCancel={() => setMemOverride(null)}
					onConfirm={handleMemOverrideConfirm}
				/>
			)}

			{/* ══ Smriti completion learning modal ══ */}
			{completeModalJob && (
				<CompleteJobModal
					job={completeModalJob}
					onCancel={() => setCompleteModalJob(null)}
					onSubmit={handleCompleteSubmit}
				/>
			)}

			{/* ══ Toasts ══ */}
			<div className="toast-container">
				{toasts.map((t) => <Toast key={t.id} message={t.msg} type={t.type} />)}
			</div>
		</div>
	);
}

/* ── Dashboard Indicator ─────────────────────────────────── */
function DI({ active, onClick, count, color, label }) {
	return (
		<button className={`dash-indicator${active ? ' dash-indicator--active' : ''}`} onClick={onClick}>
			<span className={`dash-count dash-count--${color}`}>{count}</span>
			<span className="dash-label">{label}</span>
		</button>
	);
}

/* ── Icons ─────────────────────────────────────────────── */
function RefreshIcon({ spinning }) { return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" style={spinning ? { animation: 'spin 0.8s linear infinite' } : undefined}><path d="M2.5 8a5.5 5.5 0 019.3-4M13.5 8a5.5 5.5 0 01-9.3 4" /><path d="M11.5 1v3h3M4.5 15v-3h-3" /></svg>; }
function BoltIcon() { return <svg viewBox="0 0 16 16" fill="currentColor"><path d="M9.5 1L3 9h4.5L6.5 15 13 7H8.5z" /></svg>; }
function ResetIcon({ spinning }) { return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" style={spinning ? { animation: 'spin 0.8s linear infinite' } : undefined}><path d="M13.5 8A5.5 5.5 0 1 1 8 2.5c2 0 3.8 1.1 4.8 2.7" /><path d="M13 1.5v4h-4" /></svg>; }
function BrainBtnIcon() { return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M6 2.5a2 2 0 00-2 2c-1 .3-1.7 1.2-1.7 2.3 0 .6.2 1.1.5 1.5-.3.4-.5.9-.5 1.5 0 1.2 1 2.2 2.2 2.2H6M6 2.5c.8 0 1.5.7 1.5 1.5v8c0 .8-.7 1.5-1.5 1.5M10 2.5a2 2 0 012 2c1 .3 1.7 1.2 1.7 2.3 0 .6-.2 1.1-.5 1.5.3.4.5.9.5 1.5 0 1.2-1 2.2-2.2 2.2H10M10 2.5c-.8 0-1.5.7-1.5 1.5v8c0 .8.7 1.5 1.5 1.5" /></svg>; }
function PlusIcon() { return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M8 2.5v11M2.5 8h11" /></svg>; }
function PersonPlusIcon() { return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="6.5" cy="5" r="2.5" /><path d="M2 14c0-2.6 2-4.7 4.5-4.7S11 11.4 11 14" /><path d="M12.5 5.5v4M10.5 7.5h4" /></svg>; }
