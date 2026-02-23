"""
MarketMind — Generative AI-Powered Sales & Marketing Intelligence Platform
Flask backend with Groq LLaMA 3.3 70B integration.
"""

import os
import re
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration & Database
# ---------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketmind.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------------------------------------------------------------------
# Database Models
# ---------------------------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    campaigns = db.relationship('Campaign', backref='user', lazy=True)
    pitches = db.relationship('Pitch', backref='user', lazy=True)
    leads = db.relationship('Lead', backref='user', lazy=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    cost = db.Column(db.String(100))
    audience = db.Column(db.String(200))
    platform = db.Column(db.String(100))
    result = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Pitch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(200))
    customer = db.Column(db.String(200))
    result = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    budget = db.Column(db.String(100))
    need = db.Column(db.String(200))
    urgency = db.Column(db.String(100))
    score = db.Column(db.Integer)
    probability = db.Column(db.Integer)
    analysis = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# Initialize Database safely within the application context
with app.app_context():
    db.create_all()

# ---------------------------------------------------------------------------
# Core AI Function
# ---------------------------------------------------------------------------

def call_groq(prompt: str, json_mode: bool = False) -> str:
    """Send a prompt to the Groq API and return the cleaned response text."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        }
        body = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
            
        response = requests.post(GROQ_URL, json=body, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        result = data["choices"][0]["message"]["content"]
        # Clean markdown formatting artefacts
        result = re.sub(r'[\*\\_]{2,}', '', result)
        return result
    except Exception:
        return "API error. Please try again."

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Serve the main single-page application."""
    return render_template("index.html")


@app.route("/generate_campaign", methods=["POST"])
def generate_campaign():
    """Generate a marketing campaign strategy using AI."""
    product = request.form.get("product", "")
    industry = request.form.get("industry", "")
    cost = request.form.get("cost", "")
    audience = request.form.get("audience", "")
    platform = request.form.get("platform", "")

    prompt = (
        f"Generate a detailed marketing campaign in STRICT JSON format. "
        f"Product: {product}. "
        f"Industry: {industry}. "
        f"Product Cost: {cost}. "
        f"Target Audience: {audience}. "
        f"Platform: {platform}. "
        f"Task: Evaluate the success chance if we launch this product in the specified industry at this cost point. "
        f"The JSON MUST have these keys: "
        f"'success_probability' (integer 0-100), "
        f"'target_audience' (string summary), "
        f"'content' (string with campaign objectives, 5 content ideas, 3 ad copies, and CTAs)."
    )
    output = call_groq(prompt, json_mode=True)
    
    # Save to Database
    try:
        import json
        parsed = json.loads(output)
        campaign = Campaign(
            product=product,
            industry=industry,
            cost=cost,
            audience=audience,
            platform=platform,
            result=parsed.get('content', output)
        )
        db.session.add(campaign)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error saving campaign: {e}")

    return jsonify({"result": output})


@app.route("/generate_pitch", methods=["POST"])
def generate_pitch():
    """Generate a personalised sales pitch using AI."""
    product = request.form.get("product", "")
    customer = request.form.get("customer", "")

    prompt = (
        f"Create a compelling AI sales pitch in STRICT JSON format. "
        f"Product: {product}. "
        f"Customer Persona: {customer}. "
        f"The JSON MUST have these keys: "
        f"'success_probability' (integer 0-100), "
        f"'target_audience' (string summary of persona), "
        f"'content' (string with elevator pitch, value prop, differentiators, and CTA)."
    )
    output = call_groq(prompt, json_mode=True)

    # Save to Database
    try:
        import json
        parsed = json.loads(output)
        pitch = Pitch(
            product=product,
            customer=customer,
            result=parsed.get('content', output)
        )
        db.session.add(pitch)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error saving pitch: {e}")

    return jsonify({"result": output})


@app.route("/lead_score", methods=["POST"])
def lead_score():
    """Score and qualify a lead using AI analysis."""
    name = request.form.get("name", "")
    budget = request.form.get("budget", "")
    need = request.form.get("need", "")
    urgency = request.form.get("urgency", "")

    prompt = (
        f"Score this lead based on Budget, Need, and Urgency. "
        f"Lead Name: {name}. Budget: {budget}. Need: {need}. Urgency: {urgency}. "
        f"You MUST return the output in STRICT JSON format with exactly three keys: "
        f"'score' (integer between 0 and 100), "
        f"'probability' (integer between 0 and 100 representing percentage), "
        f"and 'analysis' (string with detailed reasoning)."
    )
    output = call_groq(prompt, json_mode=True)

    # Save to Database
    try:
        import json
        parsed = json.loads(output)
        lead = Lead(
            name=name,
            budget=budget,
            need=need,
            urgency=urgency,
            score=parsed.get('score', 0),
            probability=parsed.get('probability', 0),
            analysis=parsed.get('analysis', '')
        )
        db.session.add(lead)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error saving lead score: {e}")

    return jsonify({"result": output})


# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------

@app.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    """Sign in an existing user."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Logged in successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    })


# ---------------------------------------------------------------------------
# Chatbot — Multi-turn AI Assistant
# ---------------------------------------------------------------------------

CHATBOT_SYSTEM_PROMPT = (
    "You are MarketMind Assistant, a friendly and knowledgeable AI business advisor "
    "embedded inside the MarketMind platform. MarketMind is an AI-powered Sales & "
    "Marketing Intelligence platform that helps users:\n"
    "1. Generate marketing campaigns (specify product, audience, platform)\n"
    "2. Create personalized sales pitches (specify product, customer persona)\n"
    "3. Score and qualify leads (based on budget, need, urgency)\n"
    "4. View analytics dashboards with KPI cards and interactive charts\n\n"
    "You help users with:\n"
    "- Business strategy, marketing tips, and sales techniques\n"
    "- Navigating and using the MarketMind app features\n"
    "- Interpreting analytics data and lead scores\n"
    "- General business advice and best practices\n\n"
    "Keep responses concise (2-4 sentences unless detail is requested). "
    "Be warm, professional, and actionable. Use emojis sparingly for friendliness."
)


def call_groq_chat(messages: list) -> str:
    """Send a multi-turn conversation to Groq and return the assistant reply."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        }
        full_messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}] + messages
        body = {
            "model": GROQ_MODEL,
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": 512,
        }
        response = requests.post(GROQ_URL, json=body, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        result = data["choices"][0]["message"]["content"]
        result = re.sub(r'[\*\\_]{2,}', '', result)
        return result
    except Exception:
        return "I'm having trouble connecting right now. Please try again in a moment!"


@app.route("/chatbot", methods=["POST"])
def chatbot():
    """Handle multi-turn chatbot conversations."""
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"reply": "Hi there! 👋 I'm your MarketMind Assistant. How can I help you today?"})
    reply = call_groq_chat(messages)
    return jsonify({"reply": reply})


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
