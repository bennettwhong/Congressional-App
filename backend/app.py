from flask import Flask, request, jsonify
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize OpenAI client (supports api key from environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return jsonify(message="Whisper transcription backend is running!")

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify(error="No file part in the request."), 400
    file = request.files["audio"]
    if file.filename == "":
        return jsonify(error="No file selected."), 400
    if not allowed_file(file.filename):
        return jsonify(error="Unsupported file type."), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        file.save(filepath)
        print("Saved file:", filepath)
        with open(filepath, 'rb') as audio_file:
            print("Transcribing with Whisper")
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            print("OpenAI response:", response)
            # Extract transcription text from the response object
            transcription_text = response.text
            return jsonify(transcription=transcription_text)
    except Exception as e:
        print("Error during transcription:", str(e))
        return jsonify(error=str(e)), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)  # Clean up uploaded file

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
