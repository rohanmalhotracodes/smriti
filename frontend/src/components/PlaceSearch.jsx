import { useEffect, useRef, useState } from 'react';

/**
 * PlaceSearch — Google-Maps-style location autocomplete for the map.
 *
 * Debounced geocoding via OpenStreetMap Nominatim (no API key), biased to
 * Delhi NCR and restricted to India. Picking a suggestion returns
 * { lat, lng, label } so the caller can move the map pin / fill the address.
 */
const NCR_VIEWBOX = '76.70,28.95,77.75,28.15'; // lon1,lat1,lon2,lat2 around Delhi NCR

export default function PlaceSearch({ onPick, placeholder = 'Search a place or address…' }) {
	const [query, setQuery] = useState('');
	const [results, setResults] = useState([]);
	const [open, setOpen] = useState(false);
	const [loading, setLoading] = useState(false);
	const [hi, setHi] = useState(0);
	const rootRef = useRef(null);
	const timerRef = useRef(null);
	const seqRef = useRef(0);

	useEffect(() => {
		const close = (e) => { if (!rootRef.current?.contains(e.target)) setOpen(false); };
		document.addEventListener('mousedown', close);
		return () => document.removeEventListener('mousedown', close);
	}, []);

	const search = (q) => {
		clearTimeout(timerRef.current);
		if (!q || q.trim().length < 3) { setResults([]); setLoading(false); return; }
		setLoading(true);
		timerRef.current = setTimeout(async () => {
			const seq = ++seqRef.current;
			try {
				const url = 'https://nominatim.openstreetmap.org/search?' + new URLSearchParams({
					q: q.trim(),
					format: 'jsonv2',
					countrycodes: 'in',
					viewbox: NCR_VIEWBOX,
					limit: '6',
				});
				const res = await fetch(url, { headers: { Accept: 'application/json' } });
				const data = await res.json();
				if (seq !== seqRef.current) return; // stale response
				setResults((data || []).map((r) => ({
					lat: parseFloat(r.lat),
					lng: parseFloat(r.lon),
					label: r.display_name,
				})));
				setHi(0);
				setOpen(true);
			} catch {
				if (seq === seqRef.current) setResults([]);
			} finally {
				if (seq === seqRef.current) setLoading(false);
			}
		}, 450);
	};

	const pick = (r) => {
		onPick(r);
		setQuery(r.label.split(',').slice(0, 2).join(','));
		setOpen(false);
	};

	return (
		<div className="ss-root" ref={rootRef}>
			<div className="ps-wrap">
				<SearchGlyph />
				<input
					className="ss-input ps-input"
					value={query}
					placeholder={placeholder}
					onFocus={() => results.length && setOpen(true)}
					onChange={(e) => { setQuery(e.target.value); search(e.target.value); }}
					onKeyDown={(e) => {
						if (e.key === 'ArrowDown') { e.preventDefault(); setHi((h) => Math.min(h + 1, results.length - 1)); }
						else if (e.key === 'ArrowUp') { e.preventDefault(); setHi((h) => Math.max(h - 1, 0)); }
						else if (e.key === 'Enter') { e.preventDefault(); if (open && results[hi]) pick(results[hi]); }
						else if (e.key === 'Escape') setOpen(false);
					}}
				/>
				{loading && <span className="ps-loading" />}
			</div>
			{open && results.length > 0 && (
				<div className="ss-menu">
					{results.map((r, i) => (
						<div
							key={`${r.lat},${r.lng}`}
							className={`ss-option${i === hi ? ' ss-option--hi' : ''}`}
							onMouseEnter={() => setHi(i)}
							onMouseDown={(e) => { e.preventDefault(); pick(r); }}
						>
							<span className="ps-result">{r.label}</span>
						</div>
					))}
					<div className="ps-attrib">search by OpenStreetMap Nominatim</div>
				</div>
			)}
		</div>
	);
}

function SearchGlyph() {
	return (
		<svg className="ps-glyph" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
			<circle cx="6.5" cy="6.5" r="4" /><path d="M10 10l4 4" />
		</svg>
	);
}
