// src/conf2/conf2.js
import dotenv from "dotenv";
dotenv.config();

const conf2 = {
  appwriteUrl: process.env.VITE_APPWRITE_URL,
  appwriteProjectId: process.env.VITE_APPWRITE_PROJECT_ID,
  appwriteDatabaseId: process.env.VITE_APPWRITE_DATABASE_ID,
  appwriteCollectionId: process.env.VITE_APPWRITE_COLLECTION_ID,
  appwriteNotificationCollectionId: process.env.VITE_APPWRITE_NOTIFICATION_COLLECTION_ID,
  appwriteBucketId: process.env.VITE_APPWRITE_BUCKET_ID,
  appwriteReviewSessionsCollectionId: process.env.VITE_APPWRITE_REVIEW_SESSIONS_COLLECTION_ID,
  appwriteApiKey: process.env.VITE_API_KEY,
  openApiKey: process.env.OPEN_API_KEY, // 👈 backend picks from OPENAI_API_KEY
  SMTP_USER: process.env.VITE_SMTP_USER,
  SMTP_PASS: process.env.VITE_SMTP_PASS,
};

export default conf2;
