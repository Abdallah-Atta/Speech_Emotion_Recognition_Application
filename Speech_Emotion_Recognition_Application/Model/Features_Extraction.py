import librosa
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
class FeatureExtractor:
    def __init__(self, emotion_data, n_mfcc=13):
        self.emotion_data = emotion_data
        self.n_mfcc = n_mfcc
        self.mel_features = []
        self.mfcc_features = []

    def extract_features(self):
        for i in range(len(self.emotion_data)):
            # Load the audio file
            path = self.emotion_data.loc[i, 'paths']
            data, sample_rate = librosa.load(path)

            # Extract MEL features and compute their mean
            mel = librosa.feature.melspectrogram(y=data, sr=sample_rate)
            mel_mean = np.mean(mel.T, axis=0)
            self.mel_features.append(mel_mean)

            # Extract MFCC features and compute their mean
            mfcc = librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=self.n_mfcc)
            mfcc_mean = np.mean(mfcc.T, axis=0)
            self.mfcc_features.append(mfcc_mean)

        # Convert the lists to numpy arrays
        self.mel_features_array = np.array(self.mel_features)
        self.mfcc_features_array = np.array(self.mfcc_features)

        print(f"Shape of MEL features: {self.mel_features_array.shape}")
        print(f"Shape of MFCC features: {self.mfcc_features_array.shape}")

    def combine_features(self):
        # Combine MEL and MFCC features
        self.features = np.hstack((self.mel_features_array, self.mfcc_features_array))
        print(f"Shape of combined feature data: {self.features.shape}")

    def normalize_features(self):
        # Normalize the features using StandardScaler
        self.scaler = StandardScaler()
        self.features = self.scaler.fit_transform(self.features)
        print(f"Features normalized.")
        # Save the scaler to a file for future use
        joblib.dump(self.scaler, 'Model/scaler.pkl')
        print("Scaler saved to 'scaler.pkl'.")
        return self.features
