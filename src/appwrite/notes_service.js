// src/services/notes_service.js
import axios from "axios";

const BASE_URL = "http://localhost:5000"; // change if your backend is deployed elsewhere

class NotesService {
  // --- GET NOTES ---
  async getNotes(topicId) {
    try {
      const res = await axios.get(`${BASE_URL}/topics/${topicId}/notes`);
      return res.data; // contains { notes, topic: { id, title, status } }
    } catch (err) {
      console.error("❌ NotesService :: getNotes :: error", err);
      return { notes: "", topic: null };
    }
  }

  // --- SAVE NOTES ---
  async saveNotes(topicId, notesHtml) {
    try {
      const res = await axios.post(`${BASE_URL}/topics/${topicId}/notes`, {
        notes: notesHtml,
      });
      return res.data; // { message: "Notes updated successfully" }
    } catch (err) {
      console.error("❌ NotesService :: saveNotes :: error", err);
      return false;
    }
  }
}

const notesService = new NotesService();
export default notesService;
