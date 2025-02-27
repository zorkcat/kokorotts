from flask import Flask, request, jsonify, send_file, render_template
from kokoro import KPipeline
import soundfile as sf
import os
from io import BytesIO

app = Flask(__name__, template_folder="templates")  # Explicitly set template folder

# Initialize the Kokoro TTS pipeline
pipeline = KPipeline(lang_code='a')  # 'a' = American English, adjust as needed

# Serve the frontend (root route)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# API Route: Generate Speech with Selected Voice
@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    data = request.json
    text = data.get("text", "")
    voice = data.get("voice", "af_heart")  # Default to 'af_heart' if none is selected

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Generate speech with the selected voice
    generator = pipeline(text, voice=voice, speed=1, split_pattern=r'\n+')
    audio_data = None

    for _, _, audio in generator:
        audio_data = audio

    if audio_data is None:
        return jsonify({"error": "Failed to generate audio"}), 500

    # Save audio to an in-memory file
    buffer = BytesIO()
    sf.write(buffer, audio_data, 24000, format='WAV')
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="audio/wav",
        as_attachment=False,
        download_name="output.wav"
    )

# Vercel expects a handler for serverless functions
def handler(request):
    return app(request.environ, {})

if __name__ == '__main__':
    app.run(debug=True)