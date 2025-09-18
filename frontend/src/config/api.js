// Configurazione API centralizzata - USA import.meta.env per Vite!
const isDevelopment = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const config = {
    API_URL,
    isDevelopment,
    isProduction,
    endpoints: {
        chat: `${API_URL}/api/chat`,
        health: `${API_URL}/health`,
        queue: `${API_URL}/queue`,
    }
};

// Axios instance configurata
import axios from 'axios';

export const api = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Aggiungi auth token se presente
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized
            localStorage.removeItem('token');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

export default api;