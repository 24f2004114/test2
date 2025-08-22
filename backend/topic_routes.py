from flask import Blueprint, request, jsonify
from model import db, Topic
import uuid
from datetime import datetime, timedelta
from flask_cors import CORS

topic_bp = Blueprint('topic', __name__)
CORS(topic_bp)

# === createTopic ===
@topic_bp.route('/topics', methods=['POST'])
def createTopic():
    data = request.json
    now = datetime.utcnow()

    topic = Topic(
        id=str(uuid.uuid4()),
        title=data['title'],
        notes=data.get('notes', ''),
        user_id=data['userId'],
        status=data.get('status', 'learning'),
        created_at=now,
        last_reviewed_at=data.get('lastReviewedAt', now),
        next_review_date=data.get('nextReviewAt', now + timedelta(days=1)),
        ease_factor=250,
        repetition_count=0,
        interval=1,
        test_results=[],
        weak_areas=""
    )
    db.session.add(topic)
    db.session.commit()
    return jsonify({'message': 'Topic created successfully', 'topic': topic.id})


# === getUserTopics ===
@topic_bp.route('/topics/user/<string:user_id>', methods=['GET'])
def getUserTopics(user_id):
    topics = Topic.query.filter_by(user_id=user_id).all()
    return jsonify([t.__dict__ for t in topics])


# === searchTopics ===
@topic_bp.route('/topics/search', methods=['POST'])
def searchTopics():
    data = request.json
    user_id = data['user_id']
    search_text = data['search']
    topics = Topic.query.filter(
        Topic.user_id == user_id,
        Topic.title.ilike(f"%{search_text}%")
    ).all()
    return jsonify([t.__dict__ for t in topics])


# === getTopicsByStatus ===
@topic_bp.route('/topics/status', methods=['POST'])
def getTopicsByStatus():
    data = request.json
    user_id = data['user_id']
    status = data['status']
    topics = Topic.query.filter_by(user_id=user_id, status=status).all()
    return jsonify([t.__dict__ for t in topics])


# === getTopic ===
@topic_bp.route('/topics/<string:topic_id>', methods=['GET'])
def getTopic(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    return jsonify(topic.__dict__)


# === updateTopic ===
@topic_bp.route('/topics/<string:topic_id>', methods=['PUT'])
def updateTopic(topic_id):
    data = request.json
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    for key, value in data.items():
        if hasattr(topic, key):
            setattr(topic, key, value)

    db.session.commit()
    return jsonify({'message': 'Topic updated'})


# === deleteTopic ===
@topic_bp.route('/topics/<string:topic_id>', methods=['DELETE'])
def deleteTopic(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    db.session.delete(topic)
    db.session.commit()
    return jsonify({'message': 'Topic deleted'})


# === updateTopicStatus ===
@topic_bp.route('/topics/<string:topic_id>/status', methods=['POST'])
def updateTopicStatus(topic_id):
    new_status = request.json.get("status")
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    topic.status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated'})


# === getTestResults ===
@topic_bp.route('/topics/<string:topic_id>/results', methods=['GET'])
def getTestResults(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    return jsonify(topic.test_results or [])


# === updateTopicNotes ===
@topic_bp.route('/topics/<string:topic_id>/notes', methods=['POST'])
def updateTopicNotes(topic_id):
    new_notes = request.json.get('notes')
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    topic.notes = new_notes
    db.session.commit()
    return jsonify({'message': 'Notes updated'})


# === appendTestResult ===
@topic_bp.route('/topics/<string:topic_id>/append-result', methods=['POST'])
def appendTestResult(topic_id):
    data = request.json
    new_score = data.get("score")
    weak_areas = data.get("weakAreas", [])
    topic = Topic.query.get(topic_id)

    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    # Normalize weak areas
    if isinstance(weak_areas, str):
        weak_areas = [w.strip() for w in weak_areas.split(",") if w.strip()]

    topic.test_results = (topic.test_results or []) + [new_score]
    topic.weak_areas = ", ".join(weak_areas)
    topic.last_reviewed_at = datetime.utcnow()
    topic.next_review_date = datetime.utcnow() + timedelta(days=topic.interval or 1)
    topic.repetition_count = (topic.repetition_count or 0) + 1

    db.session.commit()
    return jsonify({'message': 'Result appended'})
