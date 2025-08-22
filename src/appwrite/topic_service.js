import axios from "axios";
const BASE_URL = "http://localhost:5000/topic"; // update if hosted elsewhere

class TopicService {
  // === createTopic ===
  async createTopic({
    title,
    notes = "",
    userId,
    status = "learning",
    lastReviewedAt = null,
    nextReviewAt = null,
  }) {
    const res = await axios.post(`${BASE_URL}/topics`, {
      title,
      notes,
      userId,
      status,
      lastReviewedAt,
      nextReviewAt,
    });
    return res.data;
  }

  // === getUserTopics ===
  async getUserTopics(userId) {
    const res = await axios.get(`${BASE_URL}/topics/user/${userId}`);
    return res.data;
  }

  // === searchTopics ===
  async searchTopics(userId, searchText) {
    const res = await axios.post(`${BASE_URL}/topics/search`, {
      user_id: userId,
      search: searchText,
    });
    return res.data;
  }

  // === getTopicsByStatus ===
  async getTopicsByStatus(userId, status) {
    const res = await axios.post(`${BASE_URL}/topics/status`, {
      user_id: userId,
      status,
    });
    return res.data;
  }

  // === getTopic ===
  async getTopic(topicId) {
    const res = await axios.get(`${BASE_URL}/topics/${topicId}`);
    return res.data;
  }

  // === updateTopic ===
  async updateTopic(topicId, data) {
    const res = await axios.put(`${BASE_URL}/topics/${topicId}`, data);
    return res.data;
  }

  // === deleteTopic ===
  async deleteTopic(topicId) {
    const res = await axios.delete(`${BASE_URL}/topics/${topicId}`);
    return res.data;
  }

  // === updateTopicStatus ===
  async updateTopicStatus(topicId, newStatus) {
    const res = await axios.post(`${BASE_URL}/topics/${topicId}/status`, {
      status: newStatus,
    });
    return res.data;
  }

  // === getTestResults ===
  async getTestResults(topicId) {
    const res = await axios.get(`${BASE_URL}/topics/${topicId}/results`);
    return res.data;
  }

  // === updateTopicNotes ===
  async updateTopicNotes(topicId, newNotes) {
    const res = await axios.post(`${BASE_URL}/topics/${topicId}/notes`, {
      notes: newNotes,
    });
    return res.data;
  }

  // === appendTestResult ===
  async appendTestResult(topicId, score, weakAreas = []) {
    const res = await axios.post(`${BASE_URL}/topics/${topicId}/append-result`, {
      score,
      weakAreas,
    });
    return res.data;
  }
}

const topicService = new TopicService();
export default topicService;
