import Dashboard from '../components/Dashboard';

/** ConsolePage — the dispatch console route ("/console"). */
export default function ConsolePage({ navigate }) {
	return <Dashboard onBrandClick={() => navigate('/')} />;
}
