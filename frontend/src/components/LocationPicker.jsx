import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

/**
 * LocationPicker — embedded OpenStreetMap for the intake forms.
 *
 * Shows a pin at `position` ({lat, lng}); when `onChange` is provided the
 * map is interactive: click anywhere (or drag the pin) to set the location.
 */
export default function LocationPicker({ position, onChange, height = 180, zoom = 12 }) {
	const containerRef = useRef(null);
	const mapRef = useRef(null);
	const markerRef = useRef(null);
	const onChangeRef = useRef(onChange);
	useEffect(() => { onChangeRef.current = onChange; }, [onChange]);

	// Dot marker via DivIcon — avoids leaflet's bundler-unfriendly image assets
	const icon = useRef(L.divIcon({
		className: 'lp-pin',
		html: '<div class="lp-pin-dot"></div>',
		iconSize: [18, 18],
		iconAnchor: [9, 9],
	}));

	useEffect(() => {
		if (!containerRef.current || mapRef.current) return;
		const map = L.map(containerRef.current, {
			center: [position.lat, position.lng],
			zoom,
			zoomControl: true,
			attributionControl: false,
		});
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
		const marker = L.marker([position.lat, position.lng], {
			icon: icon.current,
			draggable: !!onChangeRef.current,
		}).addTo(map);
		if (onChangeRef.current) {
			map.on('click', (e) => {
				marker.setLatLng(e.latlng);
				onChangeRef.current?.({ lat: e.latlng.lat, lng: e.latlng.lng });
			});
			marker.on('dragend', () => {
				const ll = marker.getLatLng();
				onChangeRef.current?.({ lat: ll.lat, lng: ll.lng });
			});
		}
		mapRef.current = map;
		markerRef.current = marker;
		// Leaflet needs a size poke when mounted inside a modal
		setTimeout(() => map.invalidateSize(), 50);
		return () => { map.remove(); mapRef.current = null; };
	}, []); // eslint-disable-line

	// Follow external position changes (e.g. site/area dropdown changed)
	useEffect(() => {
		if (!mapRef.current || !markerRef.current) return;
		markerRef.current.setLatLng([position.lat, position.lng]);
		mapRef.current.setView([position.lat, position.lng], mapRef.current.getZoom());
	}, [position.lat, position.lng]);

	return <div ref={containerRef} className="lp-map" style={{ height }} />;
}
