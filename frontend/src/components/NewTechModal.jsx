import { useMemo, useState } from 'react';
import { ROUTE_AREAS, SKILLS, nearestArea } from '../data/ncr';
import { TagSearchInput } from './SearchSelect';
import LocationPicker from './LocationPicker';
import PlaceSearch from './PlaceSearch';

/**
 * NewTechModal — onboard a field technician: name, contact, skills,
 * shift, and home base. Skills are a searchable, creatable tag input
 * (the vocabulary grows with the team). Home base is set via place
 * search or a map click; the coverage area derives from the pin.
 */
export default function NewTechModal({ onCancel, onSubmit, skillSuggestions = [] }) {
	const [name, setName] = useState('');
	const [phone, setPhone] = useState('');
	const [skills, setSkills] = useState([]);
	const [shiftStart, setShiftStart] = useState('08:00');
	const [shiftEnd, setShiftEnd] = useState('17:00');
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState(null);

	// Known skills (catalog + every skill already in use on the team) —
	// the suggestion pool improves as technicians with new skills are added.
	const skillPool = [...new Set([...SKILLS, ...skillSuggestions])].sort().map((s) => ({
		value: s, label: s.replace(/_/g, ' '),
	}));
	// Home base pin — set via place search or a map click; the coverage
	// area is derived from wherever the pin lands
	const [pin, setPin] = useState({ lat: ROUTE_AREAS[0].lat, lng: ROUTE_AREAS[0].lng });
	const pinArea = useMemo(() => nearestArea(pin.lat, pin.lng), [pin.lat, pin.lng]);

	const submit = async () => {
		setError(null);
		if (!name.trim()) { setError('Name is required'); return; }
		if (skills.length === 0) { setError('Pick at least one skill'); return; }
		setSubmitting(true);
		try {
			await onSubmit({
				name: name.trim(),
				phone: phone.trim() || null,
				home_latitude: pin.lat,
				home_longitude: pin.lng,
				home_address: pinArea.name,
				skills,
				assigned_routes: [pinArea.code],
				shift_start: shiftStart,
				shift_end: shiftEnd,
			});
		} catch (e) {
			setError(e.response?.data?.detail || 'Failed to add technician');
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="override-overlay" onClick={onCancel}>
			<div className="override-modal complete-modal" onClick={(e) => e.stopPropagation()}>
				<div className="override-title">Add Technician</div>
				<div className="override-body">
					<div className="cm-grid">
						<label className="cm-field">
							<span>Full name</span>
							<input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
						</label>
						<label className="cm-field">
							<span>Phone</span>
							<input value={phone} placeholder="+91-…" onChange={(e) => setPhone(e.target.value)} />
						</label>
						<label className="cm-field">
							<span>Shift start</span>
							<input type="time" value={shiftStart} onChange={(e) => setShiftStart(e.target.value)} />
						</label>
						<label className="cm-field">
							<span>Shift end</span>
							<input type="time" value={shiftEnd} onChange={(e) => setShiftEnd(e.target.value)} />
						</label>
					</div>
					<div className="cm-field cm-field--full">
						<span>Skills — search or add new ones</span>
						<TagSearchInput
							suggestions={skillPool}
							values={skills}
							onChange={setSkills}
							placeholder="e.g. hvac, fiber, elevator…"
							allowCreate
						/>
					</div>
					<div className="cm-field cm-field--full">
						<span>Home base</span>
						<PlaceSearch onPick={(r) => setPin({ lat: r.lat, lng: r.lng })} placeholder="Search home base address…" />
						<LocationPicker position={pin} onChange={setPin} height={150} zoom={11} />
						<div className="nj-site-info">
							Coverage area: <strong>{pinArea.name}</strong> <span className="jd-mono">({pinArea.code})</span> — derived from the home base pin
						</div>
					</div>
					{error && <div className="nj-error">{error}</div>}
				</div>
				<div className="override-actions">
					<button className="btn btn--sm" onClick={onCancel}>Cancel</button>
					<button className="btn btn--sm btn--primary" onClick={submit} disabled={submitting}>
						{submitting ? 'Adding…' : 'Add technician'}
					</button>
				</div>
			</div>
		</div>
	);
}
