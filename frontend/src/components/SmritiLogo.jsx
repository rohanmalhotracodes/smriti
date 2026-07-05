/**
 * SmritiMark — the Smriti logo mark: a knowledge-graph inside a location
 * pin. Dispatch (the pin) powered by connected memory (the graph).
 */
export default function SmritiMark({ size = 17 }) {
	return (
		<svg viewBox="0 0 24 24" width={size} height={size} fill="none">
			{/* location pin */}
			<path
				d="M12 21.6c4.4-4.8 6.6-8.4 6.6-11.1a6.6 6.6 0 1 0-13.2 0c0 2.7 2.2 6.3 6.6 11.1z"
				stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"
			/>
			{/* memory graph edges */}
			<path d="M9.7 8.3l4.6-.9M9.9 8.7l1.6 3.1M14.5 7.8l-2.6 3.9" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" />
			{/* memory graph nodes */}
			<circle cx="9.3" cy="8.5" r="1.5" fill="currentColor" />
			<circle cx="14.8" cy="7.4" r="1.5" fill="currentColor" />
			<circle cx="12.1" cy="12" r="1.5" fill="currentColor" />
		</svg>
	);
}
