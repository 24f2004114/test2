from flask import Blueprint, request, jsonify
from model import db, Topic, ReviewSession
import uuid
import requests
from datetime import datetime, timedelta
import json
from flask_cors import CORS

review_bp = Blueprint('review', __name__)
CORS(review_bp) 
HUGGINGFACE_API_KEY = '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'
HUGGINGFACE_MODEL = 'moonshotai/Kimi-K2-Instruct'

# -----------------------------
# Generate Test
# -----------------------------
@review_bp.route('/generateTest/<string:topic_id>', methods=['POST'])
def generateTest(topic_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    prompt = f"""Generate 5 multiple-choice questions with 4 options each about the topic: "{topic.title}".
Return ONLY JSON array of objects:
[
  {{ "question": "string", "options": ["a","b","c","d"], "answer": "a" }}
]"""

    hfResp = requests.post(
        "https://router.huggingface.co/together/v1/completions",
        headers={
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": HUGGINGFACE_MODEL,
            "prompt": prompt,
            "max_tokens": 500
        }
    )

    hfData = hfResp.json()
    try:
        test = json.loads(hfData.get('choices', [{}])[0].get('text', "[]"))
        if not isinstance(test, list):
            raise Exception("Invalid format")
    except:
        test = [{"question": "Error generating question", "options": [], "answer": ""}]

    test = [{ "id": f"q{i+1}", **q } for i, q in enumerate(test)]

    session = ReviewSession(
        id=str(uuid.uuid4()),
        topic_id=topic_id,
        user_id=user_id,
        questions=json.dumps(test),
        answers=json.dumps([]),
        score=None,
        weaknesses="",
        recommended_next_review_at=None,
        model=HUGGINGFACE_MODEL,
        created_at=datetime.utcnow(),
        status="pending"
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "sessionId": session.id,
        "topicId": topic_id,
        "questions": test
    }), 200


# -----------------------------
# Submit / Analyze Test
# -----------------------------
@review_bp.route('/submitTest/<string:session_id>', methods=['POST'])
def analyzeTest(session_id):
    user_answers = request.json.get('answers', {})
    session = ReviewSession.query.get(session_id)

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    questions = json.loads(session.questions or "[]")
    correct = sum(1 for q in questions if user_answers.get(q["id"]) == q["answer"])
    score = round((correct / len(questions)) * 100) if questions else 0

    # Weakness prompt
    prompt = f"""The user scored {score}% on a test about "{session.topic_id}".
The test had these questions: {json.dumps(questions)}.
Based on the mistakes, provide a short list of weaknesses (as a JSON array of strings)."""

    hfResp = requests.post(
        "https://router.huggingface.co/together/v1/completions",
        headers={
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": HUGGINGFACE_MODEL,
            "prompt": prompt,
            "max_tokens": 300
        }
    )

    hfData = hfResp.json()
    try:
        parsed = json.loads(hfData.get('choices', [{}])[0].get('text', '[]'))
        weaknesses = ", ".join(parsed) if isinstance(parsed, list) else str(parsed)
    except:
        weaknesses = hfData.get('choices', [{}])[0].get('text', 'No weaknesses identified.')

    # Next review logic
    next_days = 7 if score >= 80 else 3 if score >= 50 else 1
    next_review_date = datetime.utcnow() + timedelta(days=next_days)

    # Update session
    session.answers = json.dumps(user_answers)
    session.score = score
    session.weaknesses = weaknesses
    session.recommended_next_review_at = next_review_date
    session.status = 'completed'
    db.session.commit()

    return jsonify({
        'score': score,
        'weaknesses': weaknesses,
        'nextReviewDate': next_review_date.isoformat()
    })


# -----------------------------
# Update Review Data
# -----------------------------
@review_bp.route('/updateReview/<string:topic_id>', methods=['POST'])
def updateReviewData(topic_id):
    data = request.json
    user_id = data.get("user_id")
    options = data.get("options", {})
    topic = Topic.query.get(topic_id)

    if not topic or topic.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    now = datetime.utcnow()
    nowISO = now.isoformat()
    repetition_count = topic.repetition_count or 0
    testResult = None

    if options.get("giveTest"):
        score = options.get("score", 50)
        testResult = {
            "score": score,
            "pass": score >= 50,
            "weaknesses": "N/A",
            "recommended_next_review_at": (now + timedelta(days=3)).isoformat()
        }
        session = ReviewSession(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            user_id=user_id,
            score=score,
            weaknesses=testResult["weaknesses"],
            recommended_next_review_at=testResult["recommended_next_review_at"],
            created_at=now
        )
        db.session.add(session)

    # Ease factor logic
    ease_factor = (topic.ease_factor or 250) / 100
    interval = 1

    if options.get("status"):
        status = options["status"]
        if status == "mastered":
            ease_factor = 3.0
            interval = 30
            repetition_count = 10
        elif status == "learning":
            ease_factor = 2.0
            interval = 3
            repetition_count = 3
        elif status == "forgotten":
            ease_factor = 1.3
            interval = 1
            repetition_count = 0
    else:
        repetition_count += 1
        if topic.next_review_date and topic.next_review_date < now:
            daysOverdue = (now - topic.next_review_date).days
            ease_factor = max(1.3, ease_factor - 0.2 * daysOverdue)

        if testResult:
            ease_factor = max(1.3, ease_factor + 0.1 + repetition_count * 0.05 if testResult["pass"] else ease_factor - 0.2)
        else:
            ease_factor = max(1.3, 2.5 + repetition_count * 0.05)

        if repetition_count == 1:
            interval = 1
        elif repetition_count == 2:
            interval = 6
        else:
            interval = round((topic.interval or 1) * ease_factor)

    # Calculate next review date
    if testResult:
        if testResult["score"] < 40:
            nextReviewDate = now + timedelta(days=1)
        else:
            nextReviewDate = datetime.fromisoformat(testResult["recommended_next_review_at"])
    elif options.get("status"):
        nextReviewDate = now + timedelta(days=interval)
    else:
        nextReviewDate = now + timedelta(days=interval)

    status = options.get("status")
    if not status:
        if ease_factor >= 3.0:
            status = "mastered"
        elif ease_factor >= 2.0:
            status = "learning"
        else:
            status = "forgotten"

    topic.last_reviewed_at = nowISO
    topic.next_review_date = nextReviewDate
    topic.ease_factor = round(ease_factor * 100)
    topic.repetition_count = repetition_count
    topic.interval = interval
    topic.status = status

    db.session.commit()
    return jsonify({'message': 'Review data updated successfully'}), 200
