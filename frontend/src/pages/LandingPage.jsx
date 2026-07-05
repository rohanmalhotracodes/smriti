import SmritiMark from '../components/SmritiLogo';

/**
 * LandingPage — the Smriti product homepage ("/").
 * Explains what Smriti does and routes into the dispatch console.
 */
export default function LandingPage({ navigate }) {
	const openConsole = (e) => { e.preventDefault(); navigate('/console'); };

	return (
		<div className="ld-page">
			{/* ── Nav ── */}
			<nav className="ld-nav">
				<div className="ld-brand">
					<span className="header-brand-icon header-brand-icon--smriti"><SmritiMark /></span>
					<span className="header-wordmark">Smriti</span>
				</div>
				<div className="ld-nav-links">
					<a href="#how">How it works</a>
					<a href="#memory">Memory layer</a>
					<a href="https://github.com/rohanmalhotracodes/smriti" target="_blank" rel="noreferrer">GitHub</a>
					<a href="/console" className="btn btn--primary ld-nav-cta" onClick={openConsole}>Open Console</a>
				</div>
			</nav>

			{/* ── Hero ── */}
			<header className="ld-hero">
				<div className="ld-hero-badge">स्मृति · Sanskrit for “memory” · powered by Cognee Cloud</div>
				<h1 className="ld-h1">Dispatch that <span className="ld-h1-accent">remembers</span>.</h1>
				<p className="ld-sub">
					Smriti is a memory-aware field-service dispatch platform for Indian operations.
					Every completed job teaches the system; every new ticket recalls what actually
					happened last time — which technician fixed it for good, who overran, and what
					the site never tells you until you're stuck in the lobby.
				</p>
				<div className="ld-cta-row">
					<a href="/console" className="btn btn--primary ld-cta" onClick={openConsole}>Open the dispatch console →</a>
					<a href="https://github.com/rohanmalhotracodes/smriti" target="_blank" rel="noreferrer" className="btn ld-cta">View source</a>
				</div>
				<div className="ld-stats">
					<div className="ld-stat"><strong>4</strong><span>memory operations<br />remember · recall · improve · forget</span></div>
					<div className="ld-stat"><strong>±8</strong><span>explainable scoring modifiers<br />behind every recommendation</span></div>
					<div className="ld-stat"><strong>13</strong><span>Delhi NCR service areas<br />Noida to Manesar</span></div>
				</div>
			</header>

			{/* ── Problem / story ── */}
			<section className="ld-section">
				<h2 className="ld-h2">Every dispatch system asks the same question.</h2>
				<div className="ld-compare">
					<div className="ld-compare-card">
						<div className="ld-compare-tag">Ordinary dispatch</div>
						<div className="ld-compare-q">“Who is closest and available?”</div>
						<p>
							10:47 AM — server-room cooling fails at MetroCare Tower, Cyber City.
							The router picks <strong>Aman Singh</strong>: right skills, 2.3 km away.
							Ticket closed. Except his last fix here was temporary, he's overrun
							three similar jobs, and he'll lose 30 minutes at the security desk.
						</p>
					</div>
					<div className="ld-compare-card ld-compare-card--smriti">
						<div className="ld-compare-tag ld-compare-tag--smriti">Smriti</div>
						<div className="ld-compare-q">“Who succeeded <em>here</em>, on <em>this</em>, last time?”</div>
						<p>
							Smriti recalls the site's history from Cognee: the reopened fix, the
							overruns, the pre-11AM access delays — and recommends
							<strong> Meera Iyer</strong>, who fixed five similar jobs and knows to
							call basement security before arriving. With the evidence, not a
							black box.
						</p>
					</div>
				</div>
			</section>

			{/* ── How it works ── */}
			<section className="ld-section" id="how">
				<h2 className="ld-h2">A memory lifecycle, not a chatbot.</h2>
				<p className="ld-section-sub">Smriti wires Cognee Cloud's four memory operations into the moments dispatchers actually live.</p>
				<div className="ld-grid">
					<div className="ld-card">
						<div className="ld-card-verb">remember()</div>
						<h3>Every job event becomes memory</h3>
						<p>Created, assigned, started, completed, cancelled — and every dispatcher override with its reason. Stored as structured job events plus site intelligence notes.</p>
					</div>
					<div className="ld-card">
						<div className="ld-card-verb">recall()</div>
						<h3>Recommendations with receipts</h3>
						<p>At intake, recalled history feeds an explainable scoring model: +25 similar wins in the area, −30 repeated overruns, −10 unfamiliar site with access risk. The panel shows every point.</p>
					</div>
					<div className="ld-card">
						<div className="ld-card-verb">improve()</div>
						<h3>It gets smarter — and you can watch</h3>
						<p>Complete a job and reopen the insight panel: the technician's win count and score change on the very next recall. The Memory Activity feed shows every learned event, live.</p>
					</div>
					<div className="ld-card">
						<div className="ld-card-verb">forget()</div>
						<h3>Right to be forgotten, done right</h3>
						<p>Customer offboarding or a DPDP/GDPR erasure request deletes their identifiable memory — while anonymized skill patterns survive, so compliance never lobotomizes your routing intelligence.</p>
					</div>
				</div>
			</section>

			{/* ── Memory layer detail ── */}
			<section className="ld-section" id="memory">
				<h2 className="ld-h2">Built like a product, not a demo.</h2>
				<div className="ld-grid ld-grid--3">
					<div className="ld-card ld-card--slim"><h3>Live intake</h3><p>New jobs and technicians via real forms — customer catalog, Google-Maps-style place search, searchable skills that grow with your team.</p></div>
					<div className="ld-card ld-card--slim"><h3>Two routers, side by side</h3><p>The distance router and the memory-aware router both show their pick — you see exactly when and why memory changes the decision.</p></div>
					<div className="ld-card ld-card--slim"><h3>Override accountability</h3><p>Ignore the recommendation and Smriti asks why — the reason is remembered and scored against the job's real outcome.</p></div>
					<div className="ld-card ld-card--slim"><h3>Post-job learning</h3><p>Completion captures what actually happened: duration, delay, parts, rating, fix type, watch-for-recurrence.</p></div>
					<div className="ld-card ld-card--slim"><h3>Audit trail</h3><p>Every memory operation is logged locally — what was sent to Cognee, when, and whether it landed.</p></div>
					<div className="ld-card ld-card--slim"><h3>No fake fallback</h3><p>Without Cognee credentials the memory API returns a clear configuration error. The memory is real, or it's absent.</p></div>
				</div>
			</section>

			{/* ── Final CTA ── */}
			<section className="ld-final">
				<h2 className="ld-h2">See it decide.</h2>
				<p className="ld-section-sub">The console opens pre-seeded with a Delhi NCR operation — create the 10:47 VIP emergency and watch memory flip the route.</p>
				<a href="/console" className="btn btn--primary ld-cta" onClick={openConsole}>Open the dispatch console →</a>
			</section>

			<footer className="ld-footer">
				<span>Smriti — dispatch that remembers.</span>
				<span>
					Memory by <a href="https://www.cognee.ai" target="_blank" rel="noreferrer">Cognee Cloud</a> ·
					MIT licensed ·
					demo data is synthetic
				</span>
			</footer>
		</div>
	);
}
