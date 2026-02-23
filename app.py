"""
MarketMind — Generative AI-Powered Sales & Marketing Intelligence Platform
Flask backend with Groq LLaMA 3.3 70B integration.
"""

import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

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
    audience = request.form.get("audience", "")
    platform = request.form.get("platform", "")

    prompt = (
        f"Generate a detailed marketing campaign. "
        f"Product: {product}. "
        f"Target Audience: {audience}. "
        f"Platform: {platform}. "
        f"Include: Campaign objectives, 5 targeted content ideas, "
        f"3 variations of compelling ad copy, and specific "
        f"call-to-action suggestions tailored to the platform."
    )
    output = call_groq(prompt)
    return jsonify({"result": output})


@app.route("/generate_pitch", methods=["POST"])
def generate_pitch():
    """Generate a personalised sales pitch using AI."""
    product = request.form.get("product", "")
    customer = request.form.get("customer", "")

    prompt = (
        f"Create a compelling AI sales pitch. "
        f"Product: {product}. "
        f"Customer Persona: {customer}. "
        f"Include: 30-second elevator pitch, clear value proposition, "
        f"key differentiators that address customer pain points, "
        f"and a strategic call-to-action to advance the sales process."
    )
    output = call_groq(prompt)
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
    return jsonify({"result": output})


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
