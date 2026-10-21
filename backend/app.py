import base64
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS fix: allow the deployed frontend to access the API.
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)


def get_gemini_client():
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        app.logger.warning("GEMINI_API_KEY is not configured.")
        return None

    try:
        from google import genai
        return genai.Client(api_key=key)

    except Exception:
        app.logger.exception("Could not initialize Gemini client.")
        return None


def call_gemini(prompt, image_bytes=None, mime_type="image/jpeg"):
    client = get_gemini_client()

    if not client:
        return None

    try:
        from google.genai import types

        contents = [prompt]

        if image_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
            )

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=contents,
        )

        return (
            getattr(response, "text", None)
            or "The AI returned no text."
        )

    except Exception:
        app.logger.exception("Gemini request failed.")
        return None


@app.get("/")
def home():
    return jsonify({
        "ok": True,
        "service": "Food Verse AI API",
        "health": "/api/health",
    })


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "service": "Food Verse AI API",
    })


@app.post("/api/analyze-food")
def analyze_food():
    data = request.get_json(silent=True) or {}
    image_data = data.get("image", "")

    if not image_data:
        return jsonify({
            "error": "Please upload a food image first."
        }), 400

    try:
        header, encoded = image_data.split(",", 1)
        mime_type = header.split(";")[0].split(":")[1]
        image_bytes = base64.b64decode(
            encoded,
            validate=True,
        )

    except Exception:
        return jsonify({
            "error": (
                "Image format was not recognized. "
                "Please upload the image again."
            )
        }), 400

    prompt = (
        "You are Food Verse AI, a careful food-information assistant. "
        "Analyze this image using these headings: "
        "Likely food, Visible ingredients, Approximate nutrition, "
        "Visible freshness observations, and Limitations. "
        "Clearly label nutrition values as rough estimates. "
        "Do not claim food is safe to eat based on an image. "
        "Do not invent ingredients or exact calories when uncertain. "
        "Keep the answer easy to understand."
    )

    result = call_gemini(
        prompt,
        image_bytes,
        mime_type,
    )

    if result:
        return jsonify({
            "mode": "AI",
            "result": result,
        })

    return jsonify({
        "mode": "DEMO",
        "result": (
            "The Gemini AI service is temporarily unavailable "
            "or not configured correctly. Please try again later "
            "or check the GEMINI_API_KEY and GEMINI_MODEL settings "
            "in Render.\n\n"
            "Safety note: freshness and food safety cannot be "
            "confirmed from an image alone."
        ),
    })


@app.post("/api/assistant")
def assistant():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({
            "error": "Type a question first."
        }), 400

    prompt = (
        "You are Food Verse AI, a helpful cooking and nutrition "
        "assistant. Answer clearly and concisely. For nutrition, "
        "say values are approximate unless measured. For allergies, "
        "medical diets, and food safety, recommend checking labels "
        "and qualified advice. Never guarantee food safety.\n\n"
        "User question: " + question
    )

    result = call_gemini(prompt)

    if result:
        return jsonify({
            "mode": "AI",
            "result": result,
        })

    return jsonify({
        "mode": "DEMO",
        "result": (
            "The AI service is temporarily unavailable or not "
            "configured correctly. Please try again later. "
            "Check GEMINI_API_KEY and GEMINI_MODEL in Render."
        ),
    })


@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "error": "API route not found."
    }), 404


@app.errorhandler(500)
def internal_error(_error):
    app.logger.exception("Internal server error.")

    return jsonify({
        "error": "An internal server error occurred. "
                 "Please check the backend logs."
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )