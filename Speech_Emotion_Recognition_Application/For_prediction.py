import librosa
import numpy as np
from tensorflow.keras.models import load_model
import joblib
# Preprocessing function to extract and normalize features
def preprocess_audio(file_path, scaler, n_mfcc=13):
    # Load the audio file
    data, sample_rate = librosa.load(file_path)

    # Extract MEL features
    mel = librosa.feature.melspectrogram(y=data, sr=sample_rate)
    mel_mean = np.mean(mel.T, axis=0)

    # Extract MFCC features
    mfcc = librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc.T, axis=0)

    # Combine features
    combined_features = np.hstack((mel_mean, mfcc_mean))

    # Normalize features
    normalized_features = scaler.transform([combined_features])

    # Reshape to match the model's input shape
    input_features = normalized_features.reshape(normalized_features.shape[0], normalized_features.shape[1], 1)

    return input_features

# Predict function to use the trained model and make emotion predictions
def predict_emotion(file_path, model, scaler, encoder, n_mfcc=13):
    # Preprocess the audio
    input_features = preprocess_audio(file_path, scaler, n_mfcc)

    # Predict the emotion
    predictions = model.predict(input_features)

    # Decode the one-hot prediction to the emotion label
    predicted_emotion = encoder.inverse_transform(predictions)

    return predicted_emotion[0]
