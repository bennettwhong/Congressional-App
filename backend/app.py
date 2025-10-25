from flask import Flask, request, jsonify
import os
import openai
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set up upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure OpenAI API key (from environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({"message": "Whisper transcription backend is running!"})

@app.route('/upload', methods=['POST'])
def upload_audio():
    # Verify file existence
    if 'audio' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['audio']

    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type."}), 400

    # Save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Transcribe using Whisper
    try:
        with open(filepath, 'rb') as audio_file:
            response = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return jsonify({"transcription": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

