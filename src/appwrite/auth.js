// src/services/authService.js
import axios from "axios";
import conf from "../conf/conf";  // contains backendUrl

const BASE = `${conf.backendUrl}/auth`;

const authService = {
  async createAccount({ name, email, password }) {
    const res = await axios.post(`${BASE}/createAccount`, { name, email, password });
    return res.data;
  },

  async login({ email, password }) {
    const res = await axios.post(`${BASE}/login`, { email, password });
    return res.data;
  },

  async logout() {
    await axios.post(`${BASE}/logout`);
  },

  async getCurrentUser() {
    const res = await axios.get(`${BASE}/getCurrentUser`);
    return res.data;
  },
};
export default authService;
