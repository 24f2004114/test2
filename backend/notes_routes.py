from flask import Blueprint, request, jsonify
from model import db, Topic
from flask_cors import CORS

 

notes_bp = Blueprint('notes', __name__)
CORS(notes_bp) 
# --- GET NOTES ---
@notes_bp.route('/topics/<string:topic_id>/notes', methods=['GET'])
def getNotes(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    return jsonify({
        'notes': topic.notes or "",
        'topic': {
            'id': topic.id,
            'title': topic.title,
            'status': topic.status
        }
    }), 200


# --- SAVE NOTES ---
@notes_bp.route('/topics/<string:topic_id>/notes', methods=['POST'])
def saveNotes(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    data = request.json
    notes_html = data.get('notes')
    if notes_html is None:
        return jsonify({'error': 'Missing notes field'}), 400

    topic.notes = notes_html
    db.session.commit()

    return jsonify({'message': 'Notes updated successfully'}), 200
