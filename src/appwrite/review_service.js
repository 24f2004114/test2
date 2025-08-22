import axios from "axios";

const BASE_URL = "http://localhost:5000/review";

class ReviewService {
  async generateTest(topicId) {
    try {
      const res = await axios.get(`${BASE_URL}/generate/${topicId}`);
      return res.data;
    } catch (err) {
      console.error("generateTest error:", err);
      throw err;
    }
  }

  async submitTest(sessionId, userAnswers) {
    try {
      const res = await axios.post(`${BASE_URL}/submit/${sessionId}`, {
        answers: userAnswers,
      });
      return res.data;
    } catch (err) {
      console.error("submitTest error:", err);
      throw err;
    }
  }

  async updateReviewData(topicId, userId, options = {}) {
    try {
      const res = await axios.post(`${BASE_URL}/update/${topicId}`, {
        userId,
        ...options,
      });
      return res.data;
    } catch (err) {
      console.error("updateReviewData error:", err);
      throw err;
    }
  }
}

const reviewService = new ReviewService();
export default reviewService;
