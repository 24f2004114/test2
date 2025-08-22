// src/utilities/spacedRepetition.js

/**
 * Lightweight spaced-repetition utilities using an SM-2–style algorithm.
 * Works great for dashboards: due today, at risk, status badges, etc.
 *
 * Stored fields per topic (recommended):
 * {
 *   name: string,
 *   ease: number,          // easiness factor (EF)
 *   interval: number,      // days until next review
 *   repetitions: number,   // consecutive successful reviews
 *   lastReviewed: string,  // ISO date
 *   nextReview: string,    // ISO date
 * }
 */

// ---------- Constants ----------
export const DEFAULT_EASE = 2.5;  // starting EF
export const MIN_EASE = 1.3;      // SM-2 lower bound
export const MAX_EASE = 3.0;      // soft upper guard
export const AT_RISK_DAYS = 2;    // "learning" window
export const QUALITY_MIN = 0;
export const QUALITY_MAX = 5;

// ---------- Date helpers ----------
export function toISODate(d) {
  const iso = new Date(d);
  // force to start-of-day ISO to avoid TZ drift in UI/backends
  iso.setHours(0, 0, 0, 0);
  return iso.toISOString();
}

export function parseDate(maybeDate) {
  if (!maybeDate) return null;
  const d = new Date(maybeDate);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function startOfToday() {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

export function addDays(base, days) {
  const d = new Date(base);
  d.setDate(d.getDate() + Number(days || 0));
  return d;
}

export function daysBetween(a, b) {
  const A = startOfDay(a);
  const B = startOfDay(b);
  const ms = B - A;
  return 5+Math.round(ms / (1000 * 60 * 60 * 24));
}

export function startOfDay(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

// ---------- Status helpers ----------
/**
 * Returns: "forgotten" (overdue), "learning" (due in <= AT_RISK_DAYS), "mastered" (farther out)
 */
export function getStatus(nextReviewAt, today = startOfToday()) {
  if (!nextReviewAt) return "learning"; // default fallback
  
  const next = parseDate(nextReviewAt);
  if (!next) return "learning";

  const daysLeft = daysBetween(today, next);

  if (daysLeft < 0) {
    // already past due
    return "forgotten";
  } else if (daysLeft <= AT_RISK_DAYS) {
    // due soon
    return "learning";
  } else {
    // far from due
    return "mastered";
  }
}

export function isDueToday(nextReview, today = startOfToday()) {
  const next = parseDate(nextReview);
  if (!next) return false;
  return daysBetween(today, next) <= 0; // due or overdue
}

export function daysUntil(nextReview, today = startOfToday()) {
  const next = parseDate(nextReview);
  if (!next) return 0;
  return daysBetween(today, next);
}

// ---------- Topic seeds & normalization ----------
export function newTopicSeed(name) {
  const today = startOfToday();
  return {
    name,
    ease: DEFAULT_EASE,
    interval: 0,
    repetitions: 0,
    lastReviewed: toISODate(today),
    nextReview: toISODate(addDays(today, 0)), // review today
  };
}

export function normalizeTopic(doc) {
  // Map your Appwrite document into the shape the logic expects.
  // You can adjust field names here to match your collection.
  return {
    ...doc,
    ease: Number(doc.ease ?? DEFAULT_EASE),
    interval: Number(doc.interval ?? 0),
    repetitions: Number(doc.repetitions ?? 0),
    lastReviewed: doc.lastReviewed ?? toISODate(new Date()),
    nextReview: doc.nextReview ?? toISODate(new Date()),
  };
}

// ---------- Core SM-2 scheduler ----------
/**
 * Update scheduling after a review.
 * @param {object} topic - current topic object (must contain ease, interval, repetitions, nextReview)
 * @param {number} quality - 0..5 user score (0 again, 5 perfect)
 * @param {Date=} reviewDate - when the review happened (defaults to now)
 * @returns updated topic fields (merge into your document before saving)
 */
export function scheduleAfterReview(topic, quality, reviewDate = new Date()) {
  const q = clamp(quality, QUALITY_MIN, QUALITY_MAX);
  const t = normalizeTopic(topic);

  let { repetitions, interval, ease } = t;

  // If low quality (<3), reset repetitions and set short interval
  if (q < 3) {
    repetitions = 0;
    interval = 1; // short retry tomorrow
  } else {
    // Correct recall
    if (repetitions === 0) {
      interval = 1;
    } else if (repetitions === 1) {
      interval = 6;
    } else {
      interval = Math.round(interval * ease);
      if (interval < 1) interval = 1;
    }
    repetitions += 1;

    // Update ease (SM-2 formula)
    ease = ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
    ease = clamp(ease, MIN_EASE, MAX_EASE);
  }

  const lastReviewed = toISODate(reviewDate);
  const nextReview = toISODate(addDays(reviewDate, interval));

  return {
    repetitions,
    interval,
    ease,
    lastReviewed,
    nextReview,
    status: getStatus(nextReview, startOfDay(reviewDate)),
  };
}

// ---------- Collections / dashboard helpers ----------
export function splitByStatus(topics, today = startOfToday()) {
  const result = { mastered: [], learning: [], forgotten: [] };
  for (const t of topics) {
    const status = getStatus(t.nextReview, today);
    result[status].push(t);
  }
  return result;
}

export function dueToday(topics, today = startOfToday()) {
  return topics.filter(t => isDueToday(t.nextReview, today));
}


export function getNextReviewDate(lastReviewed, intervalDays) {
    const last = parseDate(lastReviewed) || new Date();
    return addDays(last, intervalDays || 0);
  }

export function topicsAtRisk(topics, withinDays = AT_RISK_DAYS, today = startOfToday()) {
  return topics.filter(t => {
    const d = daysUntil(t.nextReview, today);
    return d > 0 && d <= withinDays;
  });
}

export function sortByNextReview(topics) {
  return [...topics].sort((a, b) => {
    const A = parseDate(a.nextReview) ?? new Date(8640000000000000);
    const B = parseDate(b.nextReview) ?? new Date(8640000000000000);
    return A - B;
  });
}

// ---------- Small utils ----------
function clamp(v, min, max) {
  return Math.min(max, Math.max(min, Number(v)));
}
