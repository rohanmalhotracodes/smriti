/**
 * Delhi NCR operating catalog — route areas, known customer sites, and
 * service categories. In production this would come from the CRM/GIS;
 * for the demo it powers the New Job and Add Technician forms.
 */

export const ROUTE_AREAS = [
	{ code: 'NOIDA-62', name: 'Noida Sector 62', lat: 28.627, lng: 77.3649 },
	{ code: 'NOIDA-18', name: 'Noida Sector 18', lat: 28.5708, lng: 77.326 },
	{ code: 'GR-NOIDA', name: 'Greater Noida', lat: 28.4744, lng: 77.504 },
	{ code: 'GHAZIABAD', name: 'Ghaziabad', lat: 28.6692, lng: 77.4538 },
	{ code: 'CP', name: 'Connaught Place', lat: 28.6315, lng: 77.2167 },
	{ code: 'SAKET', name: 'Saket', lat: 28.5245, lng: 77.21 },
	{ code: 'DWARKA', name: 'Dwarka', lat: 28.5921, lng: 77.046 },
	{ code: 'ROHINI', name: 'Rohini', lat: 28.7383, lng: 77.0822 },
	{ code: 'OKHLA', name: 'Okhla Industrial Area', lat: 28.53, lng: 77.276 },
	{ code: 'GGN-CYBER', name: 'Gurugram Cyber City', lat: 28.495, lng: 77.089 },
	{ code: 'GGN-SOHNA', name: 'Sohna Road', lat: 28.4211, lng: 77.048 },
	{ code: 'MANESAR', name: 'Manesar', lat: 28.3536, lng: 76.9391 },
	{ code: 'FARIDABAD', name: 'Faridabad Industrial Area', lat: 28.39, lng: 77.305 },
];

export const SITES = [
	{ name: 'MetroCare Tower', address: 'Tower B, DLF Cyber City', city: 'Gurugram', zip: '122002', lat: 28.4965, lng: 77.089, area: 'GGN-CYBER' },
	{ name: 'FinEdge Bank Corporate Office', address: 'Building 9A, DLF Cyber City', city: 'Gurugram', zip: '122002', lat: 28.494, lng: 77.087, area: 'GGN-CYBER' },
	{ name: 'Cyber Hub Food Court', address: 'Cyber Hub, DLF Cyber City', city: 'Gurugram', zip: '122002', lat: 28.4945, lng: 77.091, area: 'GGN-CYBER' },
	{ name: 'Vista Business Park', address: 'Sector 44, Sohna Road', city: 'Gurugram', zip: '122003', lat: 28.438, lng: 77.055, area: 'GGN-SOHNA' },
	{ name: 'BharatCloud Data Office', address: 'B-Block, Sector 62', city: 'Noida', zip: '201309', lat: 28.628, lng: 77.364, area: 'NOIDA-62' },
	{ name: 'Aarogya Hospital', address: 'Sector 62, Noida', city: 'Noida', zip: '201309', lat: 28.623, lng: 77.362, area: 'NOIDA-62' },
	{ name: 'NorthArc Mall', address: 'Sector 18, Noida', city: 'Noida', zip: '201301', lat: 28.57, lng: 77.321, area: 'NOIDA-18' },
	{ name: 'EduSphere Campus', address: 'Knowledge Park 2', city: 'Greater Noida', zip: '201310', lat: 28.47, lng: 77.51, area: 'GR-NOIDA' },
	{ name: 'CityLink Telecom Hub', address: 'Sahibabad Industrial Area', city: 'Ghaziabad', zip: '201010', lat: 28.672, lng: 77.44, area: 'GHAZIABAD' },
	{ name: 'FinEdge Bank ATM', address: 'Block A, Connaught Place', city: 'New Delhi', zip: '110001', lat: 28.632, lng: 77.218, area: 'CP' },
	{ name: 'Regal Retail Store', address: 'Block F, Connaught Place', city: 'New Delhi', zip: '110001', lat: 28.631, lng: 77.215, area: 'CP' },
	{ name: 'Apex Diagnostics', address: 'Press Enclave Road, Saket', city: 'New Delhi', zip: '110017', lat: 28.525, lng: 77.213, area: 'SAKET' },
	{ name: 'Skyline Residences', address: 'Sector 10, Dwarka', city: 'New Delhi', zip: '110075', lat: 28.587, lng: 77.05, area: 'DWARKA' },
	{ name: 'SunVolt Housing Society', address: 'Sector 19, Dwarka', city: 'New Delhi', zip: '110075', lat: 28.596, lng: 77.042, area: 'DWARKA' },
	{ name: 'Rohini Civic Centre', address: 'Sector 8, Rohini', city: 'New Delhi', zip: '110085', lat: 28.735, lng: 77.09, area: 'ROHINI' },
	{ name: 'GreenLeaf Apartments', address: 'Sector 13, Rohini', city: 'New Delhi', zip: '110085', lat: 28.725, lng: 77.105, area: 'ROHINI' },
	{ name: 'QuickCart Warehouse', address: 'Okhla Industrial Area Phase 1', city: 'New Delhi', zip: '110020', lat: 28.528, lng: 77.275, area: 'OKHLA' },
	{ name: 'PrintWorks Facility', address: 'Okhla Industrial Area Phase 3', city: 'New Delhi', zip: '110020', lat: 28.548, lng: 77.266, area: 'OKHLA' },
	{ name: 'UrbanFresh Cold Storage', address: 'IMT Manesar, Sector 8', city: 'Gurugram', zip: '122051', lat: 28.356, lng: 76.942, area: 'MANESAR' },
	{ name: 'SteelFab Works', address: 'Sector 24, Faridabad Industrial Area', city: 'Faridabad', zip: '121005', lat: 28.392, lng: 77.308, area: 'FARIDABAD' },
];

// Service categories → required skills + base job type + typical duration
export const CATEGORIES = [
	{ key: 'hvac', label: 'HVAC repair', skills: ['hvac'], jobType: 'repair', duration: 90 },
	{ key: 'hvac_elec', label: 'HVAC failure (electrical)', skills: ['hvac', 'electrical'], jobType: 'repair', duration: 90 },
	{ key: 'network', label: 'Office network outage', skills: ['network'], jobType: 'repair', duration: 60 },
	{ key: 'fiber', label: 'Telecom fiber outage', skills: ['fiber'], jobType: 'repair', duration: 120 },
	{ key: 'pos', label: 'POS terminal issue', skills: ['pos'], jobType: 'repair', duration: 45 },
	{ key: 'atm', label: 'ATM downtime', skills: ['atm'], jobType: 'repair', duration: 60 },
	{ key: 'elevator', label: 'Elevator fault', skills: ['elevator', 'electrical'], jobType: 'repair', duration: 75 },
	{ key: 'ups', label: 'Power backup / UPS failure', skills: ['ups', 'electrical'], jobType: 'repair', duration: 60 },
	{ key: 'cctv', label: 'CCTV outage', skills: ['cctv'], jobType: 'repair', duration: 45 },
	{ key: 'pump', label: 'Water pump failure', skills: ['pump'], jobType: 'repair', duration: 45 },
	{ key: 'solar', label: 'Solar inverter issue', skills: ['solar', 'electrical'], jobType: 'repair', duration: 60 },
	{ key: 'cold', label: 'Cold storage temperature alert', skills: ['cold_storage'], jobType: 'repair', duration: 75 },
	{ key: 'genset', label: 'Generator maintenance', skills: ['generator'], jobType: 'maintenance', duration: 60 },
	{ key: 'electrical', label: 'Electrical fault', skills: ['electrical'], jobType: 'repair', duration: 60 },
	{ key: 'install', label: 'New equipment install', skills: ['electrical'], jobType: 'install', duration: 90 },
	{ key: 'inspection', label: 'Inspection / compliance visit', skills: ['electrical'], jobType: 'inspection', duration: 45 },
];

export const SKILLS = [
	'hvac', 'electrical', 'network', 'fiber', 'cctv', 'atm', 'pos',
	'ups', 'elevator', 'cold_storage', 'solar', 'generator', 'pump',
];

/** Nearest service area to a coordinate (simple equirectangular distance). */
export function nearestArea(lat, lng) {
	let best = ROUTE_AREAS[0];
	let bestD = Infinity;
	for (const a of ROUTE_AREAS) {
		const d = (a.lat - lat) ** 2 + ((a.lng - lng) * 0.88) ** 2;
		if (d < bestD) { bestD = d; best = a; }
	}
	return best;
}
