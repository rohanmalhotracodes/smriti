import { useEffect, useMemo, useState } from 'react';
import { SITES, CATEGORIES, SKILLS, nearestArea } from '../data/ncr';
import LocationPicker from './LocationPicker';
import { SearchSelect, TagSearchInput } from './SearchSelect';
import PlaceSearch from './PlaceSearch';

const SITE_OPTIONS = [
	...SITES.map((s) => ({ value: s.name, label: s.name, hint: s.city })),
	{ value: '__custom__', label: 'Other customer…', hint: 'manual entry' },
];
const CATEGORY_OPTIONS = CATEGORIES.map((c) => ({ value: c.key, label: c.label }));

/**
 * NewJobModal — dispatcher intake form for an incoming service ticket.
 * Customer/site and location are ONE thing: picking a known site pins the
 * map from the CRM catalog; for a new customer, the place search sets the
 * pin + address and the service area is derived from the pin.
 */
export default function NewJobModal({ onCancel, onSubmit, skillSuggestions = [] }) {
	const [siteName, setSiteName] = useState(SITES[0].name);
	const [customSite, setCustomSite] = useState({ name: '', address: '' });
	const [categoryKey, setCategoryKey] = useState(CATEGORIES[0].key);
	const [priority, setPriority] = useState(3);
	const [slotStart, setSlotStart] = useState('');
	const [slotEnd, setSlotEnd] = useState('');
	const [description, setDescription] = useState('');
	const [instructions, setInstructions] = useState('');
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState(null);

	const isCustom = siteName === '__custom__';
	const site = useMemo(() => SITES.find((s) => s.name === siteName), [siteName]);
	const category = useMemo(() => CATEGORIES.find((c) => c.key === categoryKey), [categoryKey]);

	// One location, one pin: a known site pins from the catalog; a new
	// customer pins via place search / map click. Service area derives
	// from wherever the pin lands.
	const [pin, setPin] = useState({ lat: SITES[0].lat, lng: SITES[0].lng });
	useEffect(() => {
		if (site) setPin({ lat: site.lat, lng: site.lng });
	}, [siteName]); // eslint-disable-line
	const pinArea = useMemo(() => nearestArea(pin.lat, pin.lng), [pin.lat, pin.lng]);

	// Required skills — prefilled by the issue type, editable, and new
	// skills can be created (same growing vocabulary as technicians)
	const [reqSkills, setReqSkills] = useState(CATEGORIES[0].skills);
	useEffect(() => { if (category) setReqSkills(category.skills); }, [categoryKey]); // eslint-disable-line
	const skillPool = [...new Set([...SKILLS, ...skillSuggestions])].sort().map((s) => ({
		value: s, label: s.replace(/_/g, ' '),
	}));

	const submit = async () => {
		setError(null);
		let payload;
		if (isCustom) {
			if (!customSite.name.trim()) { setError('Customer name is required'); return; }
			payload = {
				customer_name: customSite.name.trim(),
				service_address: customSite.address.trim() || pinArea.name,
				service_city: pinArea.name,
				latitude: pin.lat,
				longitude: pin.lng,
				route_criteria: pinArea.code,
			};
		} else {
			payload = {
				customer_name: site.name,
				service_address: site.address,
				service_city: site.city,
				service_zip: site.zip,
				latitude: pin.lat,
				longitude: pin.lng,
				route_criteria: pinArea.code,
			};
		}
		const now = new Date();
		payload = {
			...payload,
			job_type: category.jobType,
			required_skills: reqSkills.length ? reqSkills : category.skills,
			priority: Number(priority),
			scheduled_date: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8).toISOString(),
			estimated_duration: category.duration,
			description: description.trim() || category.label,
		};
		if (slotStart) payload.time_slot_start = slotStart;
		if (slotEnd) payload.time_slot_end = slotEnd;
		if (instructions.trim()) payload.special_instructions = instructions.trim();

		setSubmitting(true);
		try {
			await onSubmit(payload);
		} catch (e) {
			setError(e.response?.data?.detail || 'Failed to create job');
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="override-overlay" onClick={onCancel}>
			<div className="override-modal complete-modal" onClick={(e) => e.stopPropagation()}>
				<div className="override-title">New Job</div>
				<div className="override-body">
					<div className="cm-field cm-field--full">
						<span>Customer / site — type to search</span>
						<SearchSelect options={SITE_OPTIONS} value={siteName} onChange={setSiteName} placeholder="Search customers…" autoFocus />
					</div>
					{isCustom && (
						<div className="cm-grid">
							<label className="cm-field">
								<span>Customer name</span>
								<input value={customSite.name} onChange={(e) => setCustomSite((p) => ({ ...p, name: e.target.value }))} />
							</label>
							<label className="cm-field">
								<span>Address</span>
								<input value={customSite.address} placeholder="auto-fills from map search"
									onChange={(e) => setCustomSite((p) => ({ ...p, address: e.target.value }))} />
							</label>
						</div>
					)}
					<div className="cm-field cm-field--full">
						<PlaceSearch onPick={(r) => {
							setPin({ lat: r.lat, lng: r.lng });
							if (isCustom && !customSite.address.trim()) {
								setCustomSite((p) => ({ ...p, address: r.label.split(',').slice(0, 3).join(',') }));
							}
						}} />
						<LocationPicker position={pin} onChange={setPin} height={170} zoom={isCustom ? 11 : 14} />
						<div className="nj-site-info">
							{!isCustom && <>{site.address}, {site.city} · </>}
							Service area: <strong>{pinArea.name}</strong> <span className="jd-mono">({pinArea.code})</span>
							{' '}— search above or click the map to move the pin anywhere
						</div>
					</div>
					<div className="cm-grid">
						<div className="cm-field">
							<span>Issue type — type to search</span>
							<SearchSelect options={CATEGORY_OPTIONS} value={categoryKey} onChange={setCategoryKey} placeholder="Search issue types…" />
						</div>
						<label className="cm-field">
							<span>Priority</span>
							<select value={priority} onChange={(e) => setPriority(e.target.value)}>
								<option value={1}>VIP / Emergency</option>
								<option value={2}>High</option>
								<option value={3}>Normal</option>
								<option value={4}>Low</option>
							</select>
						</label>
						<label className="cm-field">
							<span>Window start (optional)</span>
							<input type="time" value={slotStart} onChange={(e) => setSlotStart(e.target.value)} />
						</label>
						<label className="cm-field">
							<span>Window end</span>
							<input type="time" value={slotEnd} onChange={(e) => setSlotEnd(e.target.value)} />
						</label>
					</div>
					<div className="cm-field cm-field--full">
						<span>Required skills — prefilled by issue type; search or add new</span>
						<TagSearchInput
							suggestions={skillPool}
							values={reqSkills}
							onChange={setReqSkills}
							placeholder="e.g. hvac, electrical…"
							allowCreate
						/>
					</div>
					<label className="cm-field cm-field--full">
						<span>Describe the issue you are facing</span>
						<textarea rows="2" value={description} placeholder="e.g. Server room temperature rising; previous cooling issue returned"
							onChange={(e) => setDescription(e.target.value)} />
					</label>
					<label className="cm-field cm-field--full">
						<span>Special instructions (optional)</span>
						<input value={instructions} onChange={(e) => setInstructions(e.target.value)} />
					</label>
					{error && <div className="nj-error">{error}</div>}
				</div>
				<div className="override-actions">
					<button className="btn btn--sm" onClick={onCancel}>Cancel</button>
					<button className="btn btn--sm btn--primary" onClick={submit} disabled={submitting}>
						{submitting ? 'Creating…' : 'Create job'}
					</button>
				</div>
			</div>
		</div>
	);
}
