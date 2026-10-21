import base64
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

def get_gemini_client():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=key)
    except Exception:
        return None

def call_gemini(prompt, image_bytes=None, mime_type="image/jpeg"):
    client = get_gemini_client()
    if not client:
        return None
    try:
        from google.genai import types
        contents = [prompt]
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=contents
        )
        return getattr(response, "text", None) or "The AI returned no text."
    except Exception as exc:
        return f"AI service could not complete the request: {str(exc)}"

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "Food Verse AI API"})

@app.post("/api/analyze-food")
def analyze_food():
    data = request.get_json(silent=True) or {}
    image_data = data.get("image", "")
    if not image_data:
        return jsonify({"error": "Please upload a food image first."}), 400

    try:
        header, encoded = image_data.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]
        image_bytes = base64.b64decode(encoded)
    except Exception:
        return jsonify({"error": "Image format was not recognized. Please upload the image again."}), 400

    prompt = (
        "You are Food Verse AI, a careful food-information assistant. Analyze this image and answer with "
        "these headings: Likely food, Visible ingredients, Approximate nutrition (clearly label as rough estimate), "
        "Visible freshness observations, Limitations. Do not claim that food is safe to eat based on an image. "
        "Do not invent exact calories or ingredients when uncertain. Keep the answer easy to understand."
    )
    result = call_gemini(prompt, image_bytes, mime_type)
    if result:
        return jsonify({"mode": "AI", "result": result})

    return jsonify({
        "mode": "DEMO",
        "result": (
            "Demo mode is active because no working Gemini API key is configured. "
            "Your image was received successfully, but this demo does not identify the food yet. "
            "Add GEMINI_API_KEY in backend/.env to enable AI analysis.\n\n"
            "Safety note: freshness and food safety cannot be confirmed from an image alone."
        )
    })

@app.post("/api/assistant")
def assistant():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Type a question first."}), 400
    prompt = (
        "You are Food Verse AI, a helpful cooking and nutrition assistant. Answer clearly and concisely. "
        "For nutrition, say values are approximate unless measured. For allergies, medical diets, and food safety, "
        "recommend checking labels and qualified advice; never guarantee safety.\n\nUser question: " + question
    )
    result = call_gemini(prompt)
    if result:
        return jsonify({"mode": "AI", "result": result})
    return jsonify({
        "mode": "DEMO",
        "result": (
            "Demo mode: add a Gemini API key in backend/.env to enable AI answers. "
            "Try asking for a recipe using ingredients you have, or ask for a balanced meal idea."
        )
    })

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "API route not found."}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
