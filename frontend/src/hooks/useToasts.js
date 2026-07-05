import { useCallback, useRef, useState } from 'react';

/**
 * useToasts — self-contained toast queue (single responsibility:
 * transient notifications). Returns [toasts, toast].
 */
export default function useToasts(ttlMs = 3000) {
	const [toasts, setToasts] = useState([]);
	const idRef = useRef(0);

	const toast = useCallback((msg, type = 'info') => {
		const id = ++idRef.current;
		setToasts((p) => [...p, { id, msg, type }]);
		setTimeout(() => setToasts((p) => p.filter((t) => t.id !== id)), ttlMs);
	}, [ttlMs]);

	return [toasts, toast];
}
