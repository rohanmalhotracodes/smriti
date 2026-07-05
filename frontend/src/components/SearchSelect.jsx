import { useEffect, useMemo, useRef, useState } from 'react';

/**
 * SearchSelect — searchable single-select combobox.
 * Options: [{ value, label, hint? }]. Type to filter, ↑/↓ + Enter or click.
 */
export function SearchSelect({ options, value, onChange, placeholder = 'Search…', autoFocus = false }) {
	const selected = options.find((o) => o.value === value);
	const [query, setQuery] = useState('');
	const [open, setOpen] = useState(false);
	const [hi, setHi] = useState(0);
	const rootRef = useRef(null);

	const filtered = useMemo(() => {
		const q = query.trim().toLowerCase();
		if (!q) return options;
		return options.filter((o) =>
			o.label.toLowerCase().includes(q) || (o.hint || '').toLowerCase().includes(q));
	}, [options, query]);

	useEffect(() => {
		const close = (e) => { if (!rootRef.current?.contains(e.target)) setOpen(false); };
		document.addEventListener('mousedown', close);
		return () => document.removeEventListener('mousedown', close);
	}, []);

	const pick = (opt) => {
		onChange(opt.value);
		setQuery('');
		setOpen(false);
	};

	return (
		<div className="ss-root" ref={rootRef}>
			<input
				className="ss-input"
				value={open ? query : (selected?.label ?? '')}
				placeholder={selected ? selected.label : placeholder}
				autoFocus={autoFocus}
				onFocus={() => { setOpen(true); setQuery(''); setHi(0); }}
				onChange={(e) => { setQuery(e.target.value); setOpen(true); setHi(0); }}
				onKeyDown={(e) => {
					if (e.key === 'ArrowDown') { e.preventDefault(); setHi((h) => Math.min(h + 1, filtered.length - 1)); }
					else if (e.key === 'ArrowUp') { e.preventDefault(); setHi((h) => Math.max(h - 1, 0)); }
					else if (e.key === 'Enter') { e.preventDefault(); if (filtered[hi]) pick(filtered[hi]); }
					else if (e.key === 'Escape') setOpen(false);
				}}
			/>
			{open && (
				<div className="ss-menu">
					{filtered.length === 0 && <div className="ss-empty">No matches</div>}
					{filtered.map((o, i) => (
						<div
							key={o.value}
							className={`ss-option${i === hi ? ' ss-option--hi' : ''}${o.value === value ? ' ss-option--sel' : ''}`}
							onMouseEnter={() => setHi(i)}
							onMouseDown={(e) => { e.preventDefault(); pick(o); }}
						>
							<span>{o.label}</span>
							{o.hint && <span className="ss-hint">{o.hint}</span>}
						</div>
					))}
				</div>
			)}
		</div>
	);
}

/**
 * TagSearchInput — multi-select with chips + search suggestions.
 * With `allowCreate`, unknown entries can be added on the fly — so the
 * vocabulary (e.g. skills) grows over time as the team does.
 */
export function TagSearchInput({ suggestions, values, onChange, placeholder = 'Type to search…', allowCreate = false }) {
	const [query, setQuery] = useState('');
	const [open, setOpen] = useState(false);
	const [hi, setHi] = useState(0);
	const rootRef = useRef(null);

	const norm = (s) => s.trim().toLowerCase().replace(/\s+/g, '_');
	const filtered = useMemo(() => {
		const q = query.trim().toLowerCase();
		const pool = suggestions.filter((s) => !values.includes(s.value));
		const hits = q
			? pool.filter((s) => s.label.toLowerCase().includes(q) || s.value.includes(q))
			: pool;
		const canCreate = allowCreate && q && !suggestions.some((s) => s.value === norm(q)) && !values.includes(norm(q));
		return canCreate ? [...hits, { value: norm(q), label: `Add "${query.trim()}"`, create: true }] : hits;
	}, [suggestions, values, query, allowCreate]);

	useEffect(() => {
		const close = (e) => { if (!rootRef.current?.contains(e.target)) setOpen(false); };
		document.addEventListener('mousedown', close);
		return () => document.removeEventListener('mousedown', close);
	}, []);

	const add = (opt) => {
		onChange([...values, opt.value]);
		setQuery('');
	};
	const remove = (v) => onChange(values.filter((x) => x !== v));
	const labelOf = (v) => suggestions.find((s) => s.value === v)?.label ?? v.replace(/_/g, ' ');

	return (
		<div className="ss-root" ref={rootRef}>
			<div className="ts-box" onClick={() => rootRef.current?.querySelector('input')?.focus()}>
				{values.map((v) => (
					<span key={v} className="ts-tag">
						{labelOf(v)}
						<button type="button" className="ts-tag-x" onClick={() => remove(v)}>×</button>
					</span>
				))}
				<input
					className="ts-input"
					value={query}
					placeholder={values.length === 0 ? placeholder : ''}
					onFocus={() => { setOpen(true); setHi(0); }}
					onChange={(e) => { setQuery(e.target.value); setOpen(true); setHi(0); }}
					onKeyDown={(e) => {
						if (e.key === 'ArrowDown') { e.preventDefault(); setHi((h) => Math.min(h + 1, filtered.length - 1)); }
						else if (e.key === 'ArrowUp') { e.preventDefault(); setHi((h) => Math.max(h - 1, 0)); }
						else if (e.key === 'Enter') { e.preventDefault(); if (filtered[hi]) add(filtered[hi]); }
						else if (e.key === 'Backspace' && !query && values.length) remove(values[values.length - 1]);
						else if (e.key === 'Escape') setOpen(false);
					}}
				/>
			</div>
			{open && filtered.length > 0 && (
				<div className="ss-menu">
					{filtered.map((o, i) => (
						<div
							key={o.value}
							className={`ss-option${i === hi ? ' ss-option--hi' : ''}${o.create ? ' ss-option--create' : ''}`}
							onMouseEnter={() => setHi(i)}
							onMouseDown={(e) => { e.preventDefault(); add(o); }}
						>
							<span>{o.label}</span>
							{o.hint && <span className="ss-hint">{o.hint}</span>}
						</div>
					))}
				</div>
			)}
		</div>
	);
}
