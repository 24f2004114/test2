from flask import Flask
from flask_cors import CORS
from model import db
from auth_model import auth_bp
from topic_routes import topic_bp
from review_routes import review_bp  # ✅ New import

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# ================================
# Database Configuration
# ================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bunty0011:vinod#kumar222@localhost:5432/new'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ================================
# Register Blueprints
# ================================
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(topic_bp, url_prefix="/topic")
app.register_blueprint(review_bp, url_prefix="/review")  # ✅ New blueprint

# ================================
# Initialize Database (Optional)
# ================================
app.app_context().push()
def create_tables():
    with app.app_context():  # ✅ Required if you're using init_app
        db.create_all()
create_tables()
# ================================
# Health Check
# ================================
@app.route("/")
def home():
    return {"message": "LLM Tutor Backend is Running 🚀"}


@app.after_request
def apply_cors(response):
    print("✅ CORS headers being added")
    return response

# ================================
# Run App
# ================================
if __name__ == "__main__":
    app.run(debug=True)
