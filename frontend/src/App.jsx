import { useEffect, useState } from 'react';
import LandingPage from './pages/LandingPage';
import ConsolePage from './pages/ConsolePage';

/**
 * App — minimal path router: "/" is the product homepage, "/console"
 * is the dispatch console. History-API navigation, no router dependency.
 */
export default function App() {
	const [path, setPath] = useState(window.location.pathname);

	useEffect(() => {
		const onPop = () => setPath(window.location.pathname);
		window.addEventListener('popstate', onPop);
		return () => window.removeEventListener('popstate', onPop);
	}, []);

	const navigate = (to) => {
		window.history.pushState({}, '', to);
		setPath(to);
		window.scrollTo(0, 0);
	};

	if (path.startsWith('/console')) return <ConsolePage navigate={navigate} />;
	return <LandingPage navigate={navigate} />;
}
