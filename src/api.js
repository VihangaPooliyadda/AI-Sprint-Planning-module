import axios from "axios";

const api = axios.create({ baseURL: "https://your-railway-url.up.railway.app" });

export const healthCheck     = ()     => api.get("/api/health");
export const getSprintPlan   = ()     => api.get("/api/sprint-plan");
export const getSprintByNum  = (n)    => api.get(`/api/sprint-plan/${n}`);
export const getStories      = ()     => api.get("/api/stories");
export const predictPriority = (t, d) => api.post("/api/predict-priority", { title: t, description: d });
export const triggerReplan   = (data) => api.post("/api/replan", data);
export const replanFull = (data) => api.post("/api/replan-full", data);