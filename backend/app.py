import base64
import binascii
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)


def call_gemini(prompt, image_bytes=None, mime_type=None):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in Render Environment Variables."
        )

    if not model:
        raise RuntimeError(
            "GEMINI_MODEL is empty in Render Environment Variables."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    contents = [prompt]

    if image_bytes is not None:
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type or "image/jpeg",
            )
        )

    response = client.models.generate_content(
        model=model,
        contents=contents,
    )

    result = getattr(response, "text", None)

    if not result or not result.strip():
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return result.strip()


def gemini_error(error):
    # Detailed error is recorded in Render logs.
    app.logger.exception(
        "Gemini API request failed: %s",
        error,
    )

    # Return a useful error to the frontend.
    return jsonify({
        "mode": "ERROR",
        "error": str(error),
    }), 502


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

    if not isinstance(image_data, str) or not image_data:
        return jsonify({
            "error": "Please upload a food image first."
        }), 400

    try:
        header, encoded = image_data.split(",", 1)

        mime_type = header.split(";")[0].split(":")[1].lower()

        if mime_type not in (
            "image/jpeg",
            "image/png",
            "image/webp",
        ):
            return jsonify({
                "error": "Please upload a JPG, PNG, or WEBP image."
            }), 400

        image_bytes = base64.b64decode(
            encoded,
            validate=True,
        )

        if not image_bytes:
            return jsonify({
                "error": "The uploaded image is empty."
            }), 400

    except (ValueError, IndexError, binascii.Error):
        return jsonify({
            "error": "Invalid image data. Please upload the image again."
        }), 400

    prompt = """
You are Food Verse AI, a careful food-information assistant.

Analyze the provided food image using these headings:

1. Likely food
2. Visible ingredients
3. Approximate calories
4. Approximate protein, carbohydrates and fat
5. Visible freshness observations
6. Limitations

Give nutrition values as rough estimates, not exact measurements.
Mention uncertainty when portion sizes or ingredients are unclear.
Never claim that food is safe to eat based on an image.
Use simple, easy-to-understand language.
"""

    try:
        result = call_gemini(
            prompt,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )

        return jsonify({
            "mode": "AI",
            "result": result,
        })

    except Exception as error:
        return gemini_error(error)


@app.post("/api/assistant")
def assistant():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Please enter a question first."
        }), 400

    prompt = f"""
You are Food Verse AI, a helpful cooking and nutrition assistant.

Answer clearly and simply.
Give recipe ideas and practical cooking instructions when relevant.
Treat nutrition values as approximate.
For allergies, medical diets and food safety, advise checking labels
and consulting a qualified professional when necessary.
Never guarantee that food is safe to eat.

User question:
{question.strip()}
"""

    try:
        result = call_gemini(prompt)

        return jsonify({
            "mode": "AI",
            "result": result,
        })

    except Exception as error:
        return gemini_error(error)


@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "error": "API route not found."
    }), 404


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "error": "Request is too large. Please use a smaller image."
    }), 413


@app.errorhandler(500)
def internal_error(error):
    app.logger.exception("Internal server error: %s", error)

    return jsonify({
        "error": "Internal server error. Please check Render logs."
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )