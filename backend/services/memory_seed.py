"""
Smriti — synthetic historical memory seed for Cognee Cloud.

Part of the Smriti Cognee memory layer.

All records here are SYNTHETIC DEMO DATA (marked as such inside every
memory). They give Cognee the operational history that powers the demo:

  MetroCare Tower / Cyber City — 6 HVAC incidents, 2 pre-11AM access
  delays, Meera Iyer's 5 successful similar fixes, Aman Singh's 3
  overruns + 1 poor-feedback temporary fix.

  Plus supporting patterns in Noida Sector 62, Connaught Place, Okhla,
  Greater Noida, Manesar, and other Delhi NCR areas.

Seeding writes each record to the customer's own Cognee dataset (full
detail) and an anonymized copy to the shared ops-patterns dataset, so
the "forget customer" demo can delete customer memory while aggregate
patterns survive.
"""
from __future__ import annotations

import json

from backend.config import get_settings
from backend.services.cognee_memory import customer_dataset

settings = get_settings()

# Each entry: one completed historical job event.
# reopened=yes means the fix didn't hold (issue came back).
HISTORY = [
	# ═══ MetroCare Tower, Gurugram Cyber City — the demo's core site ═══
	# 6 HVAC incidents at MetroCare (3 Aman overruns, 1 Aman poor-rating temp fix,
	# 2 Meera successes) + Meera's 3 more Cyber City HVAC wins nearby = 5 similar successes.
	{
		"date": "2026-03-04", "job_type": "HVAC repair", "site": "MetroCare Tower",
		"route_area": "Gurugram Cyber City", "technician": "Aman Singh",
		"symptoms": "Server room AC unit tripping; temperature alarms on basement level 1",
		"action_taken": "Replaced contactor on CRAC unit 2; recharged gas",
		"outcome": "resolved late", "scheduled_window": "10:00-12:00",
		"duration_minutes": 210, "estimated_minutes": 90, "overran": "yes",
		"customer_rating": 3, "reopened": "no",
		"lesson": "Aman Singh overran a Cyber City HVAC compressor job by 2x the estimate",
	},
	{
		"date": "2026-03-28", "job_type": "HVAC repair", "site": "MetroCare Tower",
		"route_area": "Gurugram Cyber City", "technician": "Aman Singh",
		"symptoms": "Cooling degraded on floors 4-6; compressor service change requested",
		"action_taken": "Compressor swap attempted; parts mismatch caused rework",
		"outcome": "resolved late", "scheduled_window": "09:00-11:00",
		"duration_minutes": 240, "estimated_minutes": 120, "overran": "yes",
		"customer_rating": 3, "reopened": "no",
		"lesson": "Second overrun for Aman Singh on HVAC service-change work at MetroCare Tower",
	},
	{
		"date": "2026-04-19", "job_type": "HVAC repair", "site": "MetroCare Tower",
		"route_area": "Gurugram Cyber City", "technician": "Aman Singh",
		"symptoms": "Server room temperature rising; cooling issue recurring after March fix",
		"action_taken": "Reset condenser fault and topped up refrigerant; root cause not isolated",
		"outcome": "temporary fix", "scheduled_window": "10:00-12:00",
		"duration_minutes": 185, "estimated_minutes": 90, "overran": "yes",
		"customer_rating": 2, "reopened": "yes",
		"lesson": "Aman Singh's fix at MetroCare Tower was temporary; customer gave poor feedback when the same HVAC issue returned",
	},
	{
		"date": "2026-05-06", "job_type": "HVAC repair", "site": "MetroCare Tower",
		"route_area": "Gurugram Cyber City", "technician": "Meera Iyer",
		"symptoms": "Server room cooling failure reopened from April; temperature climbing past 27C",
		"action_taken": "Diagnosed failing condenser fan bearing; replaced fan assembly and cleaned coils",
		"outcome": "successful permanent fix", "scheduled_window": "10:00-12:00",
		"duration_minutes": 54, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Meera Iyer called basement security desk before arrival and avoided the site's access delay",
	},
	{
		"date": "2026-05-27", "job_type": "HVAC repair", "site": "MetroCare Tower",
		"route_area": "Gurugram Cyber City", "technician": "Meera Iyer",
		"symptoms": "Precision AC humidity control drifting in server room",
		"action_taken": "Recalibrated humidity sensor and replaced clogged drain line",
		"outcome": "successful permanent fix", "scheduled_window": "14:00-16:00",
		"duration_minutes": 62, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Meera Iyer is consistently fast and permanent on MetroCare Tower HVAC work",
	},
	{
		"date": "2026-06-10", "job_type": "HVAC repair", "site": "MetroCare Tower",
		"route_area": "Gurugram Cyber City", "technician": "Meera Iyer",
		"symptoms": "Quarterly follow-up on server room cooling reliability",
		"action_taken": "Preventive coil clean, verified fan replacement holding, logged runtime data",
		"outcome": "successful", "scheduled_window": "11:00-12:00",
		"duration_minutes": 45, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "MetroCare Tower server room cooling stable since Meera Iyer's permanent fix",
	},

	# Meera's other Cyber City HVAC successes (same route area, different sites)
	{
		"date": "2026-02-17", "job_type": "HVAC repair", "site": "FinEdge Bank Corporate Office",
		"route_area": "Gurugram Cyber City", "technician": "Meera Iyer",
		"symptoms": "Trading floor AC blowing warm; compressor suspected",
		"action_taken": "Replaced start capacitor and cleaned condenser; verified superheat",
		"outcome": "successful permanent fix", "scheduled_window": "09:00-11:00",
		"duration_minutes": 58, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Meera Iyer strong on Cyber City commercial HVAC compressor work",
	},
	{
		"date": "2026-04-02", "job_type": "HVAC repair", "site": "Cyber Hub Food Court",
		"route_area": "Gurugram Cyber City", "technician": "Meera Iyer",
		"symptoms": "Kitchen zone AC icing up during lunch peak",
		"action_taken": "Fixed low airflow: replaced filters and repaired blower motor wiring",
		"outcome": "successful permanent fix", "scheduled_window": "08:00-10:00",
		"duration_minutes": 65, "estimated_minutes": 75, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Meera Iyer diagnosed airflow root cause instead of just regassing",
	},

	# Aman's non-MetroCare Cyber City electrical work (he is fine at simple electrical)
	{
		"date": "2026-05-14", "job_type": "electrical fault", "site": "Cyber Hub Food Court",
		"route_area": "Gurugram Cyber City", "technician": "Aman Singh",
		"symptoms": "Distribution board tripping in food court kitchen",
		"action_taken": "Isolated faulty MCB and replaced; balanced loads",
		"outcome": "successful", "scheduled_window": "13:00-15:00",
		"duration_minutes": 50, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Aman Singh performs well on straightforward electrical faults",
	},

	# ═══ Noida Sector 62 — repeat network outage, Kabir's permanent fix ═══
	{
		"date": "2026-03-11", "job_type": "office network outage", "site": "BharatCloud Data Office",
		"route_area": "Noida Sector 62", "technician": "Karan Malhotra",
		"symptoms": "Floor 3 network down mid-afternoon; switch stack unresponsive",
		"action_taken": "Power-cycled access switch stack; service restored",
		"outcome": "temporary fix", "scheduled_window": "14:00-16:00",
		"duration_minutes": 40, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 3, "reopened": "yes",
		"lesson": "Reboot-only fix did not hold; outage pattern recurred within two weeks",
	},
	{
		"date": "2026-03-25", "job_type": "office network outage", "site": "BharatCloud Data Office",
		"route_area": "Noida Sector 62", "technician": "Kabir Arora",
		"symptoms": "Same floor 3 switch stack failing on hot afternoons",
		"action_taken": "Found switch overheating due to blocked rack vent; cleared airflow, added fan tray, replaced degraded PSU",
		"outcome": "successful permanent fix", "scheduled_window": "13:00-15:00",
		"duration_minutes": 85, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Kabir Arora found the switch-overheating root cause that repeated reboots masked",
	},
	{
		"date": "2026-04-22", "job_type": "office network outage", "site": "Aarogya Hospital",
		"route_area": "Noida Sector 62", "technician": "Kabir Arora",
		"symptoms": "Ward network drops during afternoon; core uplink flapping",
		"action_taken": "Re-terminated damaged uplink fiber and replaced SFP",
		"outcome": "successful permanent fix", "scheduled_window": "10:00-12:00",
		"duration_minutes": 70, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Kabir Arora reliable on Sector 62 network infrastructure",
	},

	# ═══ Connaught Place — ATM downtime, Priya Nair strong ═══
	{
		"date": "2026-02-09", "job_type": "ATM downtime", "site": "FinEdge Bank ATM",
		"route_area": "Connaught Place", "technician": "Priya Nair",
		"symptoms": "ATM offline; cash dispenser jam reported by branch",
		"action_taken": "Cleared dispenser jam, replaced worn pick rollers, ran 50-note test cycle",
		"outcome": "successful permanent fix", "scheduled_window": "09:00-11:00",
		"duration_minutes": 48, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Priya Nair replaces wear parts instead of only clearing ATM jams",
	},
	{
		"date": "2026-04-07", "job_type": "ATM downtime", "site": "FinEdge Bank ATM",
		"route_area": "Connaught Place", "technician": "Priya Nair",
		"symptoms": "ATM rejecting cards intermittently",
		"action_taken": "Cleaned and recalibrated card reader; updated firmware",
		"outcome": "successful", "scheduled_window": "11:00-12:00",
		"duration_minutes": 40, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Priya Nair consistently fast on Connaught Place bank hardware",
	},
	{
		"date": "2026-05-20", "job_type": "POS terminal issue", "site": "Regal Retail Store",
		"route_area": "Connaught Place", "technician": "Priya Nair",
		"symptoms": "Checkout POS terminals dropping transactions at peak hours",
		"action_taken": "Traced to faulty ethernet patching; rewired counter drops and secured PSU",
		"outcome": "successful permanent fix", "scheduled_window": "10:00-12:00",
		"duration_minutes": 55, "estimated_minutes": 75, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Priya Nair strong across retail payment hardware in CP",
	},

	# ═══ Okhla — cold storage: temporary resets failed until sensor replacement ═══
	{
		"date": "2026-03-18", "job_type": "cold storage temperature alert", "site": "QuickCart Warehouse",
		"route_area": "Okhla Industrial Area", "technician": "Nisha Verma",
		"symptoms": "Chiller room 2 temperature alarm; readings oscillating",
		"action_taken": "Controller reset; alarm cleared",
		"outcome": "temporary fix", "scheduled_window": "08:00-10:00",
		"duration_minutes": 35, "estimated_minutes": 75, "overran": "no",
		"customer_rating": 3, "reopened": "yes",
		"lesson": "Controller resets at QuickCart Warehouse do not hold; alert returned within days",
	},
	{
		"date": "2026-04-01", "job_type": "cold storage temperature alert", "site": "QuickCart Warehouse",
		"route_area": "Okhla Industrial Area", "technician": "Nisha Verma",
		"symptoms": "Repeat chiller room 2 temperature alert after reset",
		"action_taken": "Second controller reset and manual defrost",
		"outcome": "temporary fix", "scheduled_window": "09:00-11:00",
		"duration_minutes": 45, "estimated_minutes": 75, "overran": "no",
		"customer_rating": 2, "reopened": "yes",
		"lesson": "Second temporary reset at QuickCart; customer frustration rising",
	},
	{
		"date": "2026-04-15", "job_type": "cold storage temperature alert", "site": "QuickCart Warehouse",
		"route_area": "Okhla Industrial Area", "technician": "Tara Joseph",
		"symptoms": "Third chiller room 2 alert in a month",
		"action_taken": "Replaced drifting temperature sensor and recalibrated controller loop",
		"outcome": "successful permanent fix", "scheduled_window": "08:00-10:00",
		"duration_minutes": 80, "estimated_minutes": 75, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "QuickCart chiller alerts were a drifting sensor; resets were masking it — replace sensors on repeat alerts",
	},

	# ═══ Greater Noida — campus elevator faults from voltage fluctuation ═══
	{
		"date": "2026-03-07", "job_type": "elevator fault", "site": "EduSphere Campus",
		"route_area": "Greater Noida", "technician": "Rohan Batra",
		"symptoms": "Library block lift stalling between floors during morning classes",
		"action_taken": "Reset drive controller; logged supply voltage dips at 09:00-10:00",
		"outcome": "temporary fix", "scheduled_window": "09:00-11:00",
		"duration_minutes": 60, "estimated_minutes": 75, "overran": "no",
		"customer_rating": 3, "reopened": "yes",
		"lesson": "EduSphere lift faults correlate with recurring campus voltage fluctuation",
	},
	{
		"date": "2026-04-11", "job_type": "elevator fault", "site": "EduSphere Campus",
		"route_area": "Greater Noida", "technician": "Rohan Batra",
		"symptoms": "Same lift stalling; drive faulting on undervoltage",
		"action_taken": "Installed voltage stabilizer on lift supply with facilities team",
		"outcome": "successful permanent fix", "scheduled_window": "10:00-12:00",
		"duration_minutes": 95, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Voltage stabilizer resolved the recurring EduSphere elevator faults",
	},

	# ═══ Manesar — cold storage compressor + dust-clogged condensers ═══
	{
		"date": "2026-03-21", "job_type": "cold storage temperature alert", "site": "UrbanFresh Cold Storage",
		"route_area": "Manesar", "technician": "Arjun Mehta",
		"symptoms": "Compressor tripping on high head pressure in afternoon heat",
		"action_taken": "Deep-cleaned dust-clogged condenser coils; pressures normalized",
		"outcome": "successful", "scheduled_window": "10:00-12:00",
		"duration_minutes": 88, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Manesar dust clogs condenser coils fast; schedule coil cleaning proactively",
	},
	{
		"date": "2026-05-09", "job_type": "cold storage temperature alert", "site": "UrbanFresh Cold Storage",
		"route_area": "Manesar", "technician": "Arjun Mehta",
		"symptoms": "Head pressure creeping up again after summer dust storms",
		"action_taken": "Coil clean + fitted washable pre-filter screens on condenser intake",
		"outcome": "successful permanent fix", "scheduled_window": "08:00-10:00",
		"duration_minutes": 75, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Pre-filter screens cut UrbanFresh compressor trips to zero",
	},

	# ═══ Supporting NCR history (breadth for scorecards) ═══
	{
		"date": "2026-04-25", "job_type": "power backup/UPS failure", "site": "Skyline Residences",
		"route_area": "Dwarka", "technician": "Zoya Khan",
		"symptoms": "Clubhouse inverter bank not charging after outage",
		"action_taken": "Replaced failed charger card and two weak batteries",
		"outcome": "successful permanent fix", "scheduled_window": "11:00-13:00",
		"duration_minutes": 65, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Zoya Khan reliable on residential UPS banks",
	},
	{
		"date": "2026-05-16", "job_type": "solar inverter issue", "site": "SunVolt Housing Society",
		"route_area": "Dwarka", "technician": "Zoya Khan",
		"symptoms": "Rooftop array output zero after grid event",
		"action_taken": "Reset anti-islanding lockout and replaced DC isolator",
		"outcome": "successful", "scheduled_window": "10:00-12:00",
		"duration_minutes": 55, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Zoya Khan handles solar inverter protection lockouts quickly",
	},
	{
		"date": "2026-03-30", "job_type": "telecom fiber outage", "site": "CityLink Telecom Hub",
		"route_area": "Ghaziabad", "technician": "Karan Malhotra",
		"symptoms": "Trunk fiber cut near NH-24 during road work",
		"action_taken": "Spliced 48-core trunk; restored priority circuits first",
		"outcome": "successful", "scheduled_window": "08:00-12:00",
		"duration_minutes": 180, "estimated_minutes": 180, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Karan Malhotra experienced with NH-24 corridor fiber restorations",
	},
	{
		"date": "2026-05-02", "job_type": "CCTV outage", "site": "NorthArc Mall",
		"route_area": "Noida Sector 18", "technician": "Aditi Rao",
		"symptoms": "Parking level cameras offline after power maintenance",
		"action_taken": "Replaced tripped PoE injector bank and re-labelled circuits",
		"outcome": "successful permanent fix", "scheduled_window": "14:00-16:00",
		"duration_minutes": 50, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Aditi Rao knows NorthArc Mall's CCTV power layout",
	},
	{
		"date": "2026-05-23", "job_type": "POS terminal issue", "site": "NorthArc Mall",
		"route_area": "Noida Sector 18", "technician": "Aditi Rao",
		"symptoms": "Food court billing counters dropping transactions",
		"action_taken": "Isolated flaky switch port; moved counters to spare VLAN uplink",
		"outcome": "successful", "scheduled_window": "10:00-12:00",
		"duration_minutes": 45, "estimated_minutes": 45, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Aditi Rao fast on NorthArc retail systems",
	},
	{
		"date": "2026-04-29", "job_type": "generator maintenance", "site": "Rohini Civic Centre",
		"route_area": "Rohini", "technician": "Dev Sharma",
		"symptoms": "Quarterly 250 kVA DG service due",
		"action_taken": "Full service: filters, coolant, load bank test to 80%",
		"outcome": "successful", "scheduled_window": "09:00-11:00",
		"duration_minutes": 70, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Dev Sharma thorough on DG preventive maintenance",
	},
	{
		"date": "2026-05-19", "job_type": "water pump failure", "site": "GreenLeaf Apartments",
		"route_area": "Rohini", "technician": "Dev Sharma",
		"symptoms": "Basement booster pump tripping on overload",
		"action_taken": "Cleared jammed impeller and replaced worn seal",
		"outcome": "successful permanent fix", "scheduled_window": "13:00-15:00",
		"duration_minutes": 55, "estimated_minutes": 45, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Dev Sharma dependable on society pump systems",
	},
	{
		"date": "2026-04-09", "job_type": "HVAC repair", "site": "Apex Diagnostics",
		"route_area": "Saket", "technician": "Tara Joseph",
		"symptoms": "Lab cold room drifting warm; compressor short-cycling",
		"action_taken": "Replaced low-pressure switch and verified charge",
		"outcome": "successful permanent fix", "scheduled_window": "10:00-12:00",
		"duration_minutes": 60, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Tara Joseph strong on medical facility HVAC in Saket",
	},
	{
		"date": "2026-05-28", "job_type": "elevator fault", "site": "Apex Diagnostics",
		"route_area": "Saket", "technician": "Tara Joseph",
		"symptoms": "Service lift door sensor failing intermittently",
		"action_taken": "Replaced door sensor array and aligned rollers",
		"outcome": "successful", "scheduled_window": "14:00-16:00",
		"duration_minutes": 50, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Tara Joseph handles mixed HVAC/elevator sites well",
	},
	{
		"date": "2026-06-02", "job_type": "generator maintenance", "site": "SteelFab Works",
		"route_area": "Faridabad Industrial Area", "technician": "Arjun Mehta",
		"symptoms": "DG set hunting under load",
		"action_taken": "Replaced fuel filter and tuned governor",
		"outcome": "successful", "scheduled_window": "11:00-13:00",
		"duration_minutes": 65, "estimated_minutes": 60, "overran": "no",
		"customer_rating": 4, "reopened": "no",
		"lesson": "Arjun Mehta covers Faridabad generator work when Manesar is quiet",
	},
	{
		"date": "2026-06-14", "job_type": "HVAC repair", "site": "Faridabad Packaging Co",
		"route_area": "Faridabad Industrial Area", "technician": "Nisha Verma",
		"symptoms": "Shop floor AC short of cooling in summer peak",
		"action_taken": "Regassed unit; suspected slow leak not traced",
		"outcome": "temporary fix", "scheduled_window": "14:00-16:00",
		"duration_minutes": 70, "estimated_minutes": 60, "overran": "yes",
		"customer_rating": 3, "reopened": "yes",
		"lesson": "Nisha Verma tends to regas rather than leak-trace; fix expected to reopen",
	},
	{
		"date": "2026-06-20", "job_type": "office network outage", "site": "BharatCloud Data Office",
		"route_area": "Noida Sector 62", "technician": "Kabir Arora",
		"symptoms": "Planned validation visit after fan tray install",
		"action_taken": "Thermal survey of rack; confirmed switch temps 12C lower",
		"outcome": "successful", "scheduled_window": "15:00-16:00",
		"duration_minutes": 30, "estimated_minutes": 30, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Sector 62 switch-overheating pattern closed out by Kabir Arora",
	},
	{
		"date": "2026-06-18", "job_type": "power backup/UPS failure", "site": "FinEdge Bank Corporate Office",
		"route_area": "Gurugram Cyber City", "technician": "Meera Iyer",
		"symptoms": "Trading floor UPS failing self-test",
		"action_taken": "Replaced battery string and load-tested transfer switch",
		"outcome": "successful permanent fix", "scheduled_window": "09:00-11:00",
		"duration_minutes": 70, "estimated_minutes": 90, "overran": "no",
		"customer_rating": 5, "reopened": "no",
		"lesson": "Meera Iyer also covers UPS work in Cyber City towers",
	},
]

# Site/access intelligence — the "call security first" memory
SITE_NOTES = [
	{
		"date": "2026-03-04", "site": "MetroCare Tower", "route_area": "Gurugram Cyber City",
		"note_type": "access_delay",
		"details": (
			"Technician held 35 minutes at MetroCare Tower lobby before 11 AM; "
			"basement server room access card issued only after security verification. "
			"Morning shift security desk requires advance call."
		),
		"suggested_action": "Call basement security desk before arrival; ask for server room access card.",
	},
	{
		"date": "2026-04-19", "site": "MetroCare Tower", "route_area": "Gurugram Cyber City",
		"note_type": "access_delay",
		"details": (
			"Second pre-11AM access delay at MetroCare Tower: visitor gate pass system "
			"offline, technician waited 25 minutes. Security desk confirmed advance "
			"phone call bypasses lobby queue."
		),
		"suggested_action": "Call basement security desk before arrival; ask for server room access card.",
	},
	{
		"date": "2026-05-06", "site": "MetroCare Tower", "route_area": "Gurugram Cyber City",
		"note_type": "access_resolved",
		"details": (
			"Meera Iyer resolved the MetroCare Tower access/security friction: she calls the "
			"basement security desk 30 minutes before arrival and is walked straight to the "
			"server room. Zero access delay on her visits."
		),
		"suggested_action": "Meera Iyer has an established contact at the MetroCare security desk.",
	},
	{
		"date": "2026-04-15", "site": "QuickCart Warehouse", "route_area": "Okhla Industrial Area",
		"note_type": "site_pattern",
		"details": (
			"QuickCart Warehouse cold storage alerts recur when fixed by controller reset alone; "
			"sensor drift is the underlying cause. Escalate to sensor replacement on repeat alerts."
		),
		"suggested_action": "Carry replacement temperature sensors for QuickCart cold storage visits.",
	},
	{
		"date": "2026-04-11", "site": "EduSphere Campus", "route_area": "Greater Noida",
		"note_type": "site_pattern",
		"details": (
			"EduSphere Campus has recurring supply voltage fluctuation between 09:00-10:00; "
			"elevator and lab equipment faults cluster in that window."
		),
		"suggested_action": "Check supply voltage logs before replacing elevator drive parts at EduSphere.",
	},
	{
		"date": "2026-05-09", "site": "UrbanFresh Cold Storage", "route_area": "Manesar",
		"note_type": "site_pattern",
		"details": (
			"Manesar dust storms clog UrbanFresh condenser coils within weeks; compressor "
			"trips follow. Pre-filter screens fitted May 2026 need monthly wash."
		),
		"suggested_action": "Inspect condenser pre-filters on every UrbanFresh visit.",
	},
]


def _event_text(rec: dict, anonymize: bool = False) -> str:
	site = "[REDACTED SITE]" if anonymize else rec["site"]
	lines = [
		"FIELD_JOB_EVENT",
		"event_type=job_completed",
		f"date={rec['date']}",
		f"job_type={rec['job_type']}",
		f"site={site}",
		f"route_area={rec['route_area']}",
		f"technician={rec['technician']}",
		f"scheduled_window={rec['scheduled_window']}",
		f"estimated_duration_minutes={rec['estimated_minutes']}",
		f"actual_duration_minutes={rec['duration_minutes']}",
		f"overran={rec['overran']}",
		f"result={rec['outcome']}",
		f"customer_rating={rec['customer_rating']}",
		f"reopened={rec['reopened']}",
		f"symptoms={rec['symptoms']}",
		f"action_taken={rec['action_taken']}",
		f"outcome={rec['outcome']}",
		f"lesson={rec['lesson']}",
		"data_origin=synthetic demo seed (Smriti hackathon)",
	]
	metadata = {
		"kind": "field_job_event",
		"event_type": "job_completed",
		"synthetic_demo_data": True,
		"site": None if anonymize else rec["site"],
		"route_area": rec["route_area"],
		"technician": rec["technician"],
		"job_category": rec["job_type"],
		"customer_rating": rec["customer_rating"],
		"reopened": rec["reopened"] == "yes",
		"overran": rec["overran"] == "yes",
	}
	return "\n".join(lines) + "\nJSON_METADATA=" + json.dumps(metadata)


def _site_note_text(rec: dict, anonymize: bool = False) -> str:
	site = "[REDACTED SITE]" if anonymize else rec["site"]
	details = rec["details"]
	suggested = rec["suggested_action"]
	if anonymize:
		details = details.replace(rec["site"], "[REDACTED SITE]")
		suggested = suggested.replace(rec["site"], "[REDACTED SITE]")
	lines = [
		"SITE_NOTE",
		f"date={rec['date']}",
		f"site={site}",
		f"route_area={rec['route_area']}",
		f"note_type={rec['note_type']}",
		f"details={details}",
		f"suggested_action={suggested}",
		"data_origin=synthetic demo seed (Smriti hackathon)",
	]
	metadata = {
		"kind": "site_note",
		"synthetic_demo_data": True,
		"site": None if anonymize else rec["site"],
		"route_area": rec["route_area"],
		"note_type": rec["note_type"],
	}
	return "\n".join(lines) + "\nJSON_METADATA=" + json.dumps(metadata)


def build_seed_texts() -> dict[str, list[str]]:
	"""
	Build the full seed payload grouped by Cognee dataset.

	Returns {dataset_name: [memory_text, ...]}: full-detail records in each
	customer's dataset, anonymized copies in the shared ops dataset.
	"""
	by_dataset: dict[str, list[str]] = {settings.COGNEE_OPS_DATASET: []}
	for rec in HISTORY:
		ds = customer_dataset(rec["site"])
		by_dataset.setdefault(ds, []).append(_event_text(rec, anonymize=False))
		by_dataset[settings.COGNEE_OPS_DATASET].append(_event_text(rec, anonymize=True))
	for rec in SITE_NOTES:
		ds = customer_dataset(rec["site"])
		by_dataset.setdefault(ds, []).append(_site_note_text(rec, anonymize=False))
		by_dataset[settings.COGNEE_OPS_DATASET].append(_site_note_text(rec, anonymize=True))
	return by_dataset


def seed_record_count() -> int:
	return len(HISTORY) + len(SITE_NOTES)
