"""
Smriti — synthetic India (Delhi NCR) demo seed data.

All names, customers, sites, and histories are SYNTHETIC DEMO DATA
created for the Smriti hackathon demo. Any resemblance to real
persons or businesses is coincidental.

Seeded with Delhi NCR field-service operations:
technicians cover Noida, Greater Noida, Ghaziabad, Delhi, Gurugram,
Manesar, and Faridabad management areas.

Management Areas (route codes):
NOIDA-62     — Noida Sector 62
NOIDA-18     — Noida Sector 18
GR-NOIDA     — Greater Noida
GHAZIABAD    — Ghaziabad
CP           — Connaught Place, Delhi
SAKET        — Saket, South Delhi
DWARKA       — Dwarka, West Delhi
ROHINI       — Rohini, North-West Delhi
OKHLA        — Okhla Industrial Area
GGN-CYBER    — Gurugram Cyber City
GGN-SOHNA    — Sohna Road, Gurugram
MANESAR      — Manesar Industrial Area
FARIDABAD    — Faridabad Industrial Area

The demo story hinges on two Gurugram technicians:
  - Aman Singh  — closest to MetroCare Tower (Cyber City), but Cognee
                  remembers 3 HVAC overruns + 1 poor rating there.
  - Meera Iyer  — ~6 km out on Sohna Road, 5 successful similar HVAC
                  fixes in Cyber City, knows the site's security desk.

Usage:
python -m backend.database.seeds.seed_data
"""
import asyncio
from datetime import datetime, timedelta, timezone

from backend.database.connection import AsyncSessionLocal, init_db
from backend.database.models import Technician, Job, Assignment, TechnicianStatus, JobStatus, JobType

# speed_factor: global multiplier on sampled durations (1.0 = nominal)
# skill_bonuses: per-job-type multiplier, stacks with speed_factor
# These remain hidden "ground truth" — the memory layer surfaces their
# consequences (overruns, fast fixes) through recalled job history.

TECHNICIANS = [
	# ── Aman Singh — closest to Cyber City, hidden HVAC overrun pattern ──
	{
		"name": "Aman Singh",
		"employee_id": "CM-T01",
		"phone": "+91-98100-11001",
		"email": "aman.singh@crewmind.demo",
		"home_latitude": 28.5130,   # Udyog Vihar Ph-1 — ~2.2 km from MetroCare Tower
		"home_longitude": 77.0750,
		"home_address": "Udyog Vihar Phase 1, Gurugram",
		"skills": ["hvac", "electrical"],
		"assigned_routes": ["GGN-CYBER"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 1.05,
		"skill_bonuses": {"service_change": 1.35, "repair": 1.15},
	},
	# ── Meera Iyer — Sohna Road, strong Cyber City HVAC history ──
	{
		"name": "Meera Iyer",
		"employee_id": "CM-T02",
		"phone": "+91-98100-11002",
		"email": "meera.iyer@crewmind.demo",
		"home_latitude": 28.4470,   # Sohna Road — ~5.8 km from MetroCare Tower
		"home_longitude": 77.0680,
		"home_address": "Sector 48, Sohna Road, Gurugram",
		"skills": ["hvac", "electrical", "ups"],
		"assigned_routes": ["GGN-CYBER", "GGN-SOHNA"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.85,
		"skill_bonuses": {"repair": 0.85},
	},
	# ── Kabir Arora — Noida Sector 62 network specialist ──
	{
		"name": "Kabir Arora",
		"employee_id": "CM-T03",
		"phone": "+91-98100-11003",
		"email": "kabir.arora@crewmind.demo",
		"home_latitude": 28.6270,
		"home_longitude": 77.3649,
		"home_address": "Sector 62, Noida",
		"skills": ["network", "fiber", "cctv"],
		"assigned_routes": ["NOIDA-62", "GHAZIABAD"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.90,
		"skill_bonuses": {"repair": 0.88},
	},
	# ── Priya Nair — Connaught Place ATM/POS specialist ──
	{
		"name": "Priya Nair",
		"employee_id": "CM-T04",
		"phone": "+91-98100-11004",
		"email": "priya.nair@crewmind.demo",
		"home_latitude": 28.6315,
		"home_longitude": 77.2167,
		"home_address": "Connaught Place, New Delhi",
		"skills": ["atm", "pos", "electrical"],
		"assigned_routes": ["CP", "SAKET"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 9,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.88,
		"skill_bonuses": {},
	},
	# ── Nisha Verma — Okhla cold storage, history of temporary fixes ──
	{
		"name": "Nisha Verma",
		"employee_id": "CM-T05",
		"phone": "+91-98100-11005",
		"email": "nisha.verma@crewmind.demo",
		"home_latitude": 28.5300,
		"home_longitude": 77.2760,
		"home_address": "Okhla Industrial Area Phase 2, Delhi",
		"skills": ["cold_storage", "hvac"],
		"assigned_routes": ["OKHLA", "FARIDABAD"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 7,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 1.10,
		"skill_bonuses": {"repair": 1.10},
	},
	# ── Zoya Khan — Dwarka/Rohini power systems ──
	{
		"name": "Zoya Khan",
		"employee_id": "CM-T06",
		"phone": "+91-98100-11006",
		"email": "zoya.khan@crewmind.demo",
		"home_latitude": 28.5921,
		"home_longitude": 77.0460,
		"home_address": "Sector 12, Dwarka, Delhi",
		"skills": ["electrical", "ups", "solar"],
		"assigned_routes": ["DWARKA", "ROHINI"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.95,
		"skill_bonuses": {},
	},
	# ── Rohan Batra — Greater Noida elevators ──
	{
		"name": "Rohan Batra",
		"employee_id": "CM-T07",
		"phone": "+91-98100-11007",
		"email": "rohan.batra@crewmind.demo",
		"home_latitude": 28.4744,
		"home_longitude": 77.5040,
		"home_address": "Knowledge Park 3, Greater Noida",
		"skills": ["elevator", "electrical"],
		"assigned_routes": ["GR-NOIDA", "NOIDA-18"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 7,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 1.00,
		"skill_bonuses": {},
	},
	# ── Arjun Mehta — Manesar cold storage & generators ──
	{
		"name": "Arjun Mehta",
		"employee_id": "CM-T08",
		"phone": "+91-98100-11008",
		"email": "arjun.mehta@crewmind.demo",
		"home_latitude": 28.3536,
		"home_longitude": 76.9391,
		"home_address": "IMT Manesar, Gurugram",
		"skills": ["cold_storage", "generator", "hvac"],
		"assigned_routes": ["MANESAR", "GGN-SOHNA"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.97,
		"skill_bonuses": {},
	},
	# ── Karan Malhotra — Ghaziabad fiber ──
	{
		"name": "Karan Malhotra",
		"employee_id": "CM-T09",
		"phone": "+91-98100-11009",
		"email": "karan.malhotra@crewmind.demo",
		"home_latitude": 28.6692,
		"home_longitude": 77.4538,
		"home_address": "Raj Nagar Extension, Ghaziabad",
		"skills": ["fiber", "network"],
		"assigned_routes": ["GHAZIABAD", "NOIDA-62"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 1.02,
		"skill_bonuses": {},
	},
	# ── Aditi Rao — Noida Sector 18 retail systems ──
	{
		"name": "Aditi Rao",
		"employee_id": "CM-T10",
		"phone": "+91-98100-11010",
		"email": "aditi.rao@crewmind.demo",
		"home_latitude": 28.5708,
		"home_longitude": 77.3260,
		"home_address": "Sector 18, Noida",
		"skills": ["pos", "cctv", "network"],
		"assigned_routes": ["NOIDA-18", "GR-NOIDA"],
		"shift_start": "09:00",
		"shift_end": "18:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.93,
		"skill_bonuses": {},
	},
	# ── Dev Sharma — Rohini generators & pumps ──
	{
		"name": "Dev Sharma",
		"employee_id": "CM-T11",
		"phone": "+91-98100-11011",
		"email": "dev.sharma@crewmind.demo",
		"home_latitude": 28.7383,
		"home_longitude": 77.0822,
		"home_address": "Sector 7, Rohini, Delhi",
		"skills": ["generator", "electrical", "pump"],
		"assigned_routes": ["ROHINI", "CP"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 7,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 1.06,
		"skill_bonuses": {},
	},
	# ── Tara Joseph — Saket/Okhla HVAC & elevators ──
	{
		"name": "Tara Joseph",
		"employee_id": "CM-T12",
		"phone": "+91-98100-11012",
		"email": "tara.joseph@crewmind.demo",
		"home_latitude": 28.5245,
		"home_longitude": 77.2100,
		"home_address": "Saket, New Delhi",
		"skills": ["hvac", "elevator", "electrical"],
		"assigned_routes": ["SAKET", "OKHLA"],
		"shift_start": "08:00",
		"shift_end": "17:00",
		"max_jobs_per_day": 8,
		"status": TechnicianStatus.AVAILABLE,
		"speed_factor": 0.98,
		"skill_bonuses": {},
	},
]


# ── The scripted 10:47 VIP emergency (injected on demand, NOT pre-seeded) ──
VIP_EMERGENCY_JOB = {
	"job_number": "CM-VIP-1047",
	"customer_name": "MetroCare Tower",
	"customer_phone": "+91-124-450-0900",
	"service_address": "Tower B, DLF Cyber City",
	"service_city": "Gurugram",
	"service_zip": "122002",
	"latitude": 28.4965,
	"longitude": 77.0890,
	"job_type": JobType.REPAIR,
	"required_skills": ["hvac", "electrical"],
	"route_criteria": "GGN-CYBER",
	"priority": 1,
	"time_slot_start": "11:00",
	"time_slot_end": "13:00",
	"estimated_duration": 90,
	"description": "HVAC failure — server room temperature rising; previous cooling issue returned",
	"special_instructions": "VIP EMERGENCY — customer window: immediate. Server room on basement level 1.",
}


def make_jobs():
	"""
	Generate today's jobs across Delhi NCR management areas.

	NOTE: datetime.now() here is intentional — seed data needs real wall-clock
	time so today's jobs land on actual today, not simulated time.
	"""
	today = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)
	tomorrow = today + timedelta(days=1)

	return [
		# ─── GURUGRAM CYBER CITY ───
		{
			"job_number": "CM-2001",
			"customer_name": "MetroCare Tower",
			"service_address": "Tower B, DLF Cyber City",
			"service_city": "Gurugram",
			"service_zip": "122002",
			"latitude": 28.4965,
			"longitude": 77.0890,
			"job_type": JobType.MAINTENANCE,
			"required_skills": ["hvac"],
			"route_criteria": "GGN-CYBER",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "14:00",
			"time_slot_end": "16:00",
			"estimated_duration": 60,
			"description": "Quarterly HVAC filter and coil maintenance — office floors 4-6",
		},
		{
			"job_number": "CM-2002",
			"customer_name": "FinEdge Bank Corporate Office",
			"service_address": "Building 9A, DLF Cyber City",
			"service_city": "Gurugram",
			"service_zip": "122002",
			"latitude": 28.4940,
			"longitude": 77.0870,
			"job_type": JobType.REPAIR,
			"required_skills": ["ups", "electrical"],
			"route_criteria": "GGN-CYBER",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "09:00",
			"time_slot_end": "11:00",
			"estimated_duration": 60,
			"description": "UPS failure — trading floor backup power not switching over",
		},
		{
			"job_number": "CM-2003",
			"customer_name": "Cyber Hub Food Court",
			"service_address": "Cyber Hub, DLF Cyber City",
			"service_city": "Gurugram",
			"service_zip": "122002",
			"latitude": 28.4945,
			"longitude": 77.0910,
			"job_type": JobType.REPAIR,
			"required_skills": ["electrical"],
			"route_criteria": "GGN-CYBER",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "13:00",
			"time_slot_end": "15:00",
			"estimated_duration": 45,
			"description": "Kitchen exhaust panel tripping — intermittent breaker fault",
		},

		# ─── SOHNA ROAD ───
		{
			"job_number": "CM-2004",
			"customer_name": "Vista Business Park",
			"service_address": "Sector 44, Sohna Road",
			"service_city": "Gurugram",
			"service_zip": "122003",
			"latitude": 28.4380,
			"longitude": 77.0550,
			"job_type": JobType.MAINTENANCE,
			"required_skills": ["hvac", "electrical"],
			"route_criteria": "GGN-SOHNA",
			"priority": 4,
			"scheduled_date": today,
			"time_slot_start": "08:00",
			"time_slot_end": "10:00",
			"estimated_duration": 45,
			"description": "AHU belt inspection and preventive maintenance",
		},

		# ─── NOIDA SECTOR 62 ───
		{
			"job_number": "CM-2005",
			"customer_name": "BharatCloud Data Office",
			"service_address": "B-Block, Sector 62",
			"service_city": "Noida",
			"service_zip": "201309",
			"latitude": 28.6280,
			"longitude": 77.3640,
			"job_type": JobType.REPAIR,
			"required_skills": ["network"],
			"route_criteria": "NOIDA-62",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "09:00",
			"time_slot_end": "11:00",
			"estimated_duration": 60,
			"description": "Office network outage — access switch stack unresponsive on floor 3",
		},
		{
			"job_number": "CM-2006",
			"customer_name": "Aarogya Hospital",
			"service_address": "Sector 62, Noida",
			"service_city": "Noida",
			"service_zip": "201309",
			"latitude": 28.6230,
			"longitude": 77.3620,
			"job_type": JobType.INSPECTION,
			"required_skills": ["cctv"],
			"route_criteria": "NOIDA-62",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "11:00",
			"time_slot_end": "13:00",
			"estimated_duration": 45,
			"description": "CCTV outage — ICU corridor cameras offline, compliance inspection due",
		},

		# ─── NOIDA SECTOR 18 ───
		{
			"job_number": "CM-2007",
			"customer_name": "NorthArc Mall",
			"service_address": "Sector 18, Noida",
			"service_city": "Noida",
			"service_zip": "201301",
			"latitude": 28.5700,
			"longitude": 77.3210,
			"job_type": JobType.REPAIR,
			"required_skills": ["pos"],
			"route_criteria": "NOIDA-18",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "10:00",
			"time_slot_end": "12:00",
			"estimated_duration": 45,
			"description": "POS terminal issue — food court billing counters dropping transactions",
		},
		{
			"job_number": "CM-2008",
			"customer_name": "NorthArc Mall",
			"service_address": "Sector 18, Noida",
			"service_city": "Noida",
			"service_zip": "201301",
			"latitude": 28.5702,
			"longitude": 77.3215,
			"job_type": JobType.MAINTENANCE,
			"required_skills": ["cctv", "network"],
			"route_criteria": "NOIDA-18",
			"priority": 4,
			"scheduled_date": today,
			"time_slot_start": "14:00",
			"time_slot_end": "16:00",
			"estimated_duration": 60,
			"description": "Parking level CCTV preventive maintenance — 4 cameras flagged degraded",
		},

		# ─── GREATER NOIDA ───
		{
			"job_number": "CM-2009",
			"customer_name": "EduSphere Campus",
			"service_address": "Knowledge Park 2",
			"service_city": "Greater Noida",
			"service_zip": "201310",
			"latitude": 28.4700,
			"longitude": 77.5100,
			"job_type": JobType.REPAIR,
			"required_skills": ["elevator", "electrical"],
			"route_criteria": "GR-NOIDA",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "09:00",
			"time_slot_end": "11:00",
			"estimated_duration": 75,
			"description": "Elevator fault — library block lift stalling between floors 2-3",
		},

		# ─── GHAZIABAD ───
		{
			"job_number": "CM-2010",
			"customer_name": "CityLink Telecom Hub",
			"service_address": "Sahibabad Industrial Area",
			"service_city": "Ghaziabad",
			"service_zip": "201010",
			"latitude": 28.6720,
			"longitude": 77.4400,
			"job_type": JobType.REPAIR,
			"required_skills": ["fiber"],
			"route_criteria": "GHAZIABAD",
			"priority": 1,
			"scheduled_date": today,
			"time_slot_start": "08:00",
			"time_slot_end": "10:00",
			"estimated_duration": 90,
			"description": "Telecom fiber outage — trunk cut near NH-24 crossing, 3 exchanges degraded",
		},

		# ─── CONNAUGHT PLACE ───
		{
			"job_number": "CM-2011",
			"customer_name": "FinEdge Bank ATM",
			"service_address": "Block A, Connaught Place",
			"service_city": "New Delhi",
			"service_zip": "110001",
			"latitude": 28.6320,
			"longitude": 77.2180,
			"job_type": JobType.REPAIR,
			"required_skills": ["atm"],
			"route_criteria": "CP",
			"priority": 1,
			"scheduled_date": today,
			"time_slot_start": "09:00",
			"time_slot_end": "11:00",
			"estimated_duration": 60,
			"description": "ATM downtime — cash dispenser jam, third incident this quarter",
		},
		{
			"job_number": "CM-2012",
			"customer_name": "Regal Retail Store",
			"service_address": "Block F, Connaught Place",
			"service_city": "New Delhi",
			"service_zip": "110001",
			"latitude": 28.6310,
			"longitude": 77.2150,
			"job_type": JobType.INSTALL,
			"required_skills": ["pos", "electrical"],
			"route_criteria": "CP",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "13:00",
			"time_slot_end": "15:00",
			"estimated_duration": 75,
			"description": "New POS terminal install — 3 checkout counters",
		},

		# ─── SAKET ───
		{
			"job_number": "CM-2013",
			"customer_name": "Apex Diagnostics",
			"service_address": "Press Enclave Road, Saket",
			"service_city": "New Delhi",
			"service_zip": "110017",
			"latitude": 28.5250,
			"longitude": 77.2130,
			"job_type": JobType.REPAIR,
			"required_skills": ["hvac"],
			"route_criteria": "SAKET",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "10:00",
			"time_slot_end": "12:00",
			"estimated_duration": 60,
			"description": "Lab cold room temperature drift — HVAC compressor short-cycling",
		},

		# ─── DWARKA ───
		{
			"job_number": "CM-2014",
			"customer_name": "Skyline Residences",
			"service_address": "Sector 10, Dwarka",
			"service_city": "New Delhi",
			"service_zip": "110075",
			"latitude": 28.5870,
			"longitude": 77.0500,
			"job_type": JobType.REPAIR,
			"required_skills": ["ups", "electrical"],
			"route_criteria": "DWARKA",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "11:00",
			"time_slot_end": "13:00",
			"estimated_duration": 60,
			"description": "Power backup/UPS failure — society clubhouse inverter bank not charging",
		},
		{
			"job_number": "CM-2015",
			"customer_name": "SunVolt Housing Society",
			"service_address": "Sector 19, Dwarka",
			"service_city": "New Delhi",
			"service_zip": "110075",
			"latitude": 28.5960,
			"longitude": 77.0420,
			"job_type": JobType.REPAIR,
			"required_skills": ["solar", "electrical"],
			"route_criteria": "DWARKA",
			"priority": 4,
			"scheduled_date": today,
			"time_slot_start": "14:00",
			"time_slot_end": "16:00",
			"estimated_duration": 60,
			"description": "Solar inverter issue — rooftop array feeding zero output since morning",
		},

		# ─── ROHINI ───
		{
			"job_number": "CM-2016",
			"customer_name": "Rohini Civic Centre",
			"service_address": "Sector 8, Rohini",
			"service_city": "New Delhi",
			"service_zip": "110085",
			"latitude": 28.7350,
			"longitude": 77.0900,
			"job_type": JobType.MAINTENANCE,
			"required_skills": ["generator"],
			"route_criteria": "ROHINI",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "09:00",
			"time_slot_end": "11:00",
			"estimated_duration": 60,
			"description": "Generator maintenance — 250 kVA DG set quarterly service",
		},
		{
			"job_number": "CM-2017",
			"customer_name": "GreenLeaf Apartments",
			"service_address": "Sector 13, Rohini",
			"service_city": "New Delhi",
			"service_zip": "110085",
			"latitude": 28.7250,
			"longitude": 77.1050,
			"job_type": JobType.REPAIR,
			"required_skills": ["pump"],
			"route_criteria": "ROHINI",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "13:00",
			"time_slot_end": "15:00",
			"estimated_duration": 45,
			"description": "Water pump failure — basement booster pump tripping on overload",
		},

		# ─── OKHLA ───
		{
			"job_number": "CM-2018",
			"customer_name": "QuickCart Warehouse",
			"service_address": "Okhla Industrial Area Phase 1",
			"service_city": "New Delhi",
			"service_zip": "110020",
			"latitude": 28.5280,
			"longitude": 77.2750,
			"job_type": JobType.REPAIR,
			"required_skills": ["cold_storage"],
			"route_criteria": "OKHLA",
			"priority": 1,
			"scheduled_date": today,
			"time_slot_start": "08:00",
			"time_slot_end": "10:00",
			"estimated_duration": 75,
			"description": "Cold storage temperature alert — chiller room 2 rising past 8°C",
		},
		{
			"job_number": "CM-2019",
			"customer_name": "PrintWorks Facility",
			"service_address": "Okhla Industrial Area Phase 3",
			"service_city": "New Delhi",
			"service_zip": "110020",
			"latitude": 28.5480,
			"longitude": 77.2660,
			"job_type": JobType.INSPECTION,
			"required_skills": ["electrical"],
			"route_criteria": "OKHLA",
			"priority": 4,
			"scheduled_date": today,
			"time_slot_start": "15:00",
			"time_slot_end": "17:00",
			"estimated_duration": 45,
			"description": "Annual electrical panel thermal inspection",
		},

		# ─── MANESAR ───
		{
			"job_number": "CM-2020",
			"customer_name": "UrbanFresh Cold Storage",
			"service_address": "IMT Manesar, Sector 8",
			"service_city": "Gurugram",
			"service_zip": "122051",
			"latitude": 28.3560,
			"longitude": 76.9420,
			"job_type": JobType.MAINTENANCE,
			"required_skills": ["cold_storage", "hvac"],
			"route_criteria": "MANESAR",
			"priority": 2,
			"scheduled_date": today,
			"time_slot_start": "10:00",
			"time_slot_end": "12:00",
			"estimated_duration": 90,
			"description": "Compressor condenser coil cleaning — dust clogging flagged last visit",
		},

		# ─── FARIDABAD ───
		{
			"job_number": "CM-2021",
			"customer_name": "SteelFab Works",
			"service_address": "Sector 24, Faridabad Industrial Area",
			"service_city": "Faridabad",
			"service_zip": "121005",
			"latitude": 28.3920,
			"longitude": 77.3080,
			"job_type": JobType.REPAIR,
			"required_skills": ["generator", "electrical"],
			"route_criteria": "FARIDABAD",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "11:00",
			"time_slot_end": "13:00",
			"estimated_duration": 60,
			"description": "DG set not taking load during power cut — AVR suspected",
		},
		{
			"job_number": "CM-2022",
			"customer_name": "Faridabad Packaging Co",
			"service_address": "Sector 25, Faridabad Industrial Area",
			"service_city": "Faridabad",
			"service_zip": "121005",
			"latitude": 28.3860,
			"longitude": 77.3150,
			"job_type": JobType.REPAIR,
			"required_skills": ["hvac"],
			"route_criteria": "FARIDABAD",
			"priority": 3,
			"scheduled_date": today,
			"time_slot_start": "14:00",
			"time_slot_end": "16:00",
			"estimated_duration": 60,
			"description": "Shop floor AC units short of cooling — gas pressure check",
		},

		# ─── TOMORROW (light load for day-picker) ───
		{
			"job_number": "CM-2101",
			"customer_name": "Aarogya Hospital",
			"service_address": "Sector 62, Noida",
			"service_city": "Noida",
			"service_zip": "201309",
			"latitude": 28.6230,
			"longitude": 77.3620,
			"job_type": JobType.MAINTENANCE,
			"required_skills": ["hvac"],
			"route_criteria": "NOIDA-62",
			"priority": 2,
			"scheduled_date": tomorrow,
			"time_slot_start": "09:00",
			"time_slot_end": "11:00",
			"estimated_duration": 90,
			"description": "OT wing HVAC deep service — scheduled downtime window",
		},
		{
			"job_number": "CM-2102",
			"customer_name": "MetroCare Tower",
			"service_address": "Tower B, DLF Cyber City",
			"service_city": "Gurugram",
			"service_zip": "122002",
			"latitude": 28.4965,
			"longitude": 77.0890,
			"job_type": JobType.INSPECTION,
			"required_skills": ["electrical"],
			"route_criteria": "GGN-CYBER",
			"priority": 3,
			"scheduled_date": tomorrow,
			"time_slot_start": "10:00",
			"time_slot_end": "12:00",
			"estimated_duration": 45,
			"description": "Basement electrical room compliance inspection",
		},
		{
			"job_number": "CM-2103",
			"customer_name": "CityLink Telecom Hub",
			"service_address": "Sahibabad Industrial Area",
			"service_city": "Ghaziabad",
			"service_zip": "201010",
			"latitude": 28.6720,
			"longitude": 77.4400,
			"job_type": JobType.INSTALL,
			"required_skills": ["fiber", "network"],
			"route_criteria": "GHAZIABAD",
			"priority": 3,
			"scheduled_date": tomorrow,
			"time_slot_start": "09:00",
			"time_slot_end": "12:00",
			"estimated_duration": 120,
			"description": "New OLT rack install and fiber patching",
		},
	]


async def seed_all():
	"""Drop existing data and seed fresh India demo data."""
	await init_db()

	async with AsyncSessionLocal() as session:
		print("\n🇮🇳 Seeding Smriti with Delhi NCR demo data...\n")

		# Clear existing data (order matters — assignments first)
		from sqlalchemy import text
		await session.execute(text("DELETE FROM assignments"))
		await session.execute(text("DELETE FROM jobs"))
		await session.execute(text("DELETE FROM technicians"))
		await session.commit()
		print("  ✓ Cleared existing data")

		# Seed technicians
		for tech_data in TECHNICIANS:
			tech = Technician(
				**tech_data,
				current_latitude=tech_data["home_latitude"],
				current_longitude=tech_data["home_longitude"],
			)
			session.add(tech)
		await session.commit()
		print(f"  ✓ {len(TECHNICIANS)} technicians seeded")

		jobs_data = make_jobs()
		for job_data in jobs_data:
			job = Job(**job_data)
			session.add(job)
		await session.commit()
		print(f"  ✓ {len(jobs_data)} jobs seeded")

		print("\n✅ Done! Delhi NCR demo day ready. Inject the 10:47 VIP emergency from the demo panel.\n")


if __name__ == "__main__":
	asyncio.run(seed_all())
