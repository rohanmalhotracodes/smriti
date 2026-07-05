import { useState } from 'react';

/**
 * CompleteJobModal — post-job learning capture (Smriti layer).
 *
 * On completion the dispatcher records what actually happened; the
 * backend stores it locally and feeds Cognee (remember + improve).
 */
export default function CompleteJobModal({ job, onCancel, onSubmit }) {
	const [form, setForm] = useState({
		actual_duration_minutes: job?.estimated_duration || 60,
		arrival_delay_minutes: 0,
		resolution_notes: '',
		parts_used: '',
		customer_rating: 5,
		fix_type: 'permanent',
		watch_recurrence: false,
	});
	const [submitting, setSubmitting] = useState(false);

	const set = (k, v) => setForm((p) => ({ ...p, [k]: v }));

	const submit = async () => {
		setSubmitting(true);
		try {
			await onSubmit({
				...form,
				actual_duration_minutes: Number(form.actual_duration_minutes) || null,
				arrival_delay_minutes: Number(form.arrival_delay_minutes) || 0,
				resolution_notes: form.resolution_notes || null,
				parts_used: form.parts_used || null,
			});
		} finally {
			setSubmitting(false);
		}
	};

	if (!job) return null;

	return (
		<div className="override-overlay" onClick={onCancel}>
			<div className="override-modal complete-modal" onClick={(e) => e.stopPropagation()}>
				<div className="override-title">Complete Job #{job.job_number || job.id} — what actually happened?</div>
				<div className="override-body">
					<div className="cm-grid">
						<label className="cm-field">
							<span>Actual duration (min)</span>
							<input type="number" min="1" value={form.actual_duration_minutes}
								onChange={(e) => set('actual_duration_minutes', e.target.value)} />
						</label>
						<label className="cm-field">
							<span>Arrival delay (min)</span>
							<input type="number" min="0" value={form.arrival_delay_minutes}
								onChange={(e) => set('arrival_delay_minutes', e.target.value)} />
						</label>
						<label className="cm-field">
							<span>Customer rating</span>
							<select value={form.customer_rating} onChange={(e) => set('customer_rating', Number(e.target.value))}>
								{[5, 4, 3, 2, 1].map((r) => <option key={r} value={r}>{'★'.repeat(r)}{'☆'.repeat(5 - r)}</option>)}
							</select>
						</label>
						<label className="cm-field">
							<span>Fix type</span>
							<select value={form.fix_type} onChange={(e) => set('fix_type', e.target.value)}>
								<option value="permanent">Permanent</option>
								<option value="temporary">Temporary</option>
								<option value="workaround">Workaround</option>
							</select>
						</label>
					</div>
					<label className="cm-field cm-field--full">
						<span>Resolution notes</span>
						<textarea rows="2" value={form.resolution_notes} placeholder="What was done, root cause…"
							onChange={(e) => set('resolution_notes', e.target.value)} />
					</label>
					<label className="cm-field cm-field--full">
						<span>Parts used</span>
						<input type="text" value={form.parts_used} placeholder="e.g. condenser fan relay"
							onChange={(e) => set('parts_used', e.target.value)} />
					</label>
					<label className="cm-check">
						<input type="checkbox" checked={form.watch_recurrence}
							onChange={(e) => set('watch_recurrence', e.target.checked)} />
						Watch this issue for recurrence
					</label>
				</div>
				<div className="override-actions">
					<button className="btn btn--sm" onClick={onCancel}>Cancel</button>
					<button className="btn btn--sm btn--primary" onClick={submit} disabled={submitting}>
						{submitting ? 'Completing…' : 'Complete & teach Cognee'}
					</button>
				</div>
			</div>
		</div>
	);
}
