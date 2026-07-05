import axios from 'axios';

// Use relative path so it works on any domain/IP
const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		'Content-Type': 'application/json',
	},
});

export const api = {
	// Technicians
	getTechnicians: () => apiClient.get('/technicians/'),
	createTechnician: (data) => apiClient.post('/technicians/', data),
	updateTechStatus: (id, status) => apiClient.patch(`/technicians/${id}/status`, { status }),

	// Jobs
	getJobs: (params = {}) => apiClient.get('/jobs/', { params }),
	getJob: (id) => apiClient.get(`/jobs/${id}`),
	createJob: (data) => apiClient.post('/jobs/', data),
	getJobsSummary: (params = {}) => apiClient.get('/jobs/summary', { params }),
	startJob: (jobId) => apiClient.post(`/jobs/${jobId}/start`, {}),
	completeJobWithOutcome: (jobId, data = {}) => apiClient.post(`/jobs/${jobId}/complete`, data),
	cancelJob: (jobId) => apiClient.post(`/jobs/${jobId}/cancel`, {}),
	updateJobStatus: (jobId, status) => apiClient.patch(`/jobs/${jobId}/status`, { status }),

	// Assignments
	unassignJob: (jobId) => apiClient.post('/assignments/unassign', { job_id: jobId }),
	batchAssign: (jobIds, techId) => apiClient.post('/assignments/batch-assign', {
		job_ids: jobIds,
		technician_id: techId,
	}),
	batchUnassign: (jobIds) => apiClient.post('/assignments/batch-unassign', {
		job_ids: jobIds,
	}),

	// Routing (base)
	autoRoute: (data = {}) => apiClient.post('/routing/auto-route', data),

	// Smriti — Cognee memory layer
	memoryStatus: () => apiClient.get('/memory/status'),
	jobInsights: (jobId) => apiClient.get(`/memory/jobs/${jobId}/insights`, { timeout: 180000 }),
	rememberOverride: (jobId, data) => apiClient.post(`/memory/jobs/${jobId}/override`, data, { timeout: 300000 }),
	forgetCustomer: (customerName) => apiClient.post('/memory/customers/forget', { customer_name: customerName, confirm: true }, { timeout: 300000 }),
	memoryEvents: (limit = 12) => apiClient.get('/memory/events', { params: { limit } }),
};

export default api;
