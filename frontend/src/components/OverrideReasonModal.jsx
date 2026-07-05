import { useState } from 'react';

/**
 * OverrideReasonModal — shown when the dispatcher assigns a different
 * technician than the memory-aware recommendation (Smriti layer).
 * The reason is stored in Cognee as a DISPATCH_OVERRIDE memory and
 * improved with the real outcome when the job completes.
 */
const REASONS = [
	'Customer requested this technician',
	'Technician has local knowledge',
	'Emergency proximity',
	'Manager instruction',
	'Skill mismatch in recommendation',
	'Other',
];

export default function OverrideReasonModal({ techName, recommendedName, onCancel, onConfirm }) {
	const [reason, setReason] = useState(REASONS[2]);
	const [other, setOther] = useState('');
	const [submitting, setSubmitting] = useState(false);

	const confirm = async () => {
		setSubmitting(true);
		try {
			await onConfirm(reason === 'Other' ? (other || 'Other') : reason);
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="override-overlay" onClick={onCancel}>
			<div className="override-modal" onClick={(e) => e.stopPropagation()}>
				<div className="override-title">Why are you overriding the memory-aware recommendation?</div>
				<div className="override-body">
					<div className="ov-summary">
						Cognee recommends <strong>{recommendedName}</strong> — you are assigning{' '}
						<strong>{techName}</strong>. This override will be remembered and scored
						against the job's actual outcome.
					</div>
					<div className="ov-reasons">
						{REASONS.map((r) => (
							<label key={r} className="ov-reason">
								<input type="radio" name="ov-reason" checked={reason === r} onChange={() => setReason(r)} />
								{r}
							</label>
						))}
						{reason === 'Other' && (
							<input
								type="text" className="ov-other" placeholder="Describe the reason…"
								value={other} onChange={(e) => setOther(e.target.value)} autoFocus
							/>
						)}
					</div>
				</div>
				<div className="override-actions">
					<button className="btn btn--sm" onClick={onCancel}>Cancel</button>
					<button className="btn btn--sm btn--warning" onClick={confirm} disabled={submitting}>
						{submitting ? 'Assigning…' : 'Override & remember'}
					</button>
				</div>
			</div>
		</div>
	);
}
