from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)  # or UUID if you're using that
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.VarChar(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    topics = db.relationship('Topic', backref='user', lazy=True)
    review_sessions = db.relationship('ReviewSession', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String, nullable=False)
    notes = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    last_reviewed_at = db.Column(db.DateTime)
    next_review_date = db.Column(db.DateTime, nullable=False)
    
    ease_factor = db.Column(db.Integer)
    repetition_count = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)

    test_results = db.Column(db.ARRAY(db.Integer))  # Use array for Double[]
    important = db.Column(db.Boolean, default=False)
    lapse = db.Column(db.Integer, default=0)
    weak_areas = db.Column(db.String)

    review_sessions = db.relationship('ReviewSession', backref='topic', lazy=True)




class ReviewSession(db.Model):
    __tablename__ = 'review_sessions'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.String, db.ForeignKey('topics.id'), nullable=False)

    score = db.Column(db.Integer)
    recommended_next_review_at = db.Column(db.DateTime)
    model = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now())

    status = db.Column(db.String, default='pending')
    questions = db.Column(db.ARRAY(db.String))  # Array of strings
    answers = db.Column(db.ARRAY(db.String))
    weaknesses = db.Column(db.String)



