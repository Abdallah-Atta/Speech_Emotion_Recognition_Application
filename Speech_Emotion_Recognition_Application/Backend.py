from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from conn import *
from tensorflow.keras.models import load_model
from For_prediction import predict_emotion
import joblib
import numpy as np

app = Flask(__name__)

# Directory to store uploaded files
UPLOAD_FOLDER = r"D:\AI\deep_learning\Final_project\myApp\uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Supported file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Endpoint to upload audio (recording or file upload)
@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file and save the record to the database."""
    user_id = request.form.get('user_id')  # Get user ID from form data

    # Validate the user_id
    if not user_id or not user_id.isdigit():
        return jsonify({"error": "Invalid or missing user ID"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save record to the database
        if not save_record(user_id, file_path):
            return jsonify({"error": "Failed to save record in database"}), 500

        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    else:
        return jsonify({"error": "Invalid file type. Only wav and mp3 are allowed."}), 400

# Endpoint to retrieve a user's recordings
@app.route('/recordings/<user_id>', methods=['GET'])
def get_recordings(user_id):
    """Get all recordings for a specific user."""
    if not user_id.isdigit():
        return jsonify({"error" : "Invalid user ID"}), 400

    recordings = get_user_records(user_id)
    if not recordings:
        return jsonify({"error": "No recordings found for this user"}), 404

    # Formatting the response with readable data
    response = [{"id": record[0], "cloud_link": record[1], "file_path": record[2], "timestamp": record[3]} for record in recordings]
    return jsonify({"recordings": response}), 200

# Endpoint to play a specific recording
@app.route('/play/<filename>', methods=['GET'])
def play_file(filename):
    """Serve the requested file for playback."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


@app.route('/predict', methods=['POST'])
def predict():
    """Predict the result from the uploaded audio file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Predict using the loaded model
        try:
            # Load required components
            scaler = joblib.load("Model\scaler.pkl")
            print("Scaler loaded")
            encoder = joblib.load("Model\encoder.pkl")
            print("Encoder loaded")
            trained_model = load_model('Model\speech_emotion_cnn_model.keras')
            print("Model loaded")

            # Make prediction
            predicted_emotion = predict_emotion(file_path, trained_model, scaler, encoder)
            print(f"Predicted emotion: {predicted_emotion}")

            # If the result needs further processing, adjust here

            return jsonify({"prediction": predicted_emotion[0]}), 200
        except Exception as e:
            print(f"Prediction failed: {str(e)}")
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Only wav and mp3 are allowed."}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)




