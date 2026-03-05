import axios from "axios";

// In dev: use empty baseURL so requests go through Vite proxy (avoids CORS + 404)
// In prod: set VITE_API_BASE to your backend URL (e.g. https://api.example.com)
const baseURL = import.meta.env.VITE_API_BASE ?? "";

export const api = axios.create({
  baseURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const forecastApi = {
  getHistory: () => api.get("/forecast/history"),
  clearHistory: () => api.delete("/forecast/history"),
};

// Dashboard related helpers
export const computeMi = (coin, options = {}) => api.post(`/dashboard/metadata/${coin}/compute_mi`, options);

