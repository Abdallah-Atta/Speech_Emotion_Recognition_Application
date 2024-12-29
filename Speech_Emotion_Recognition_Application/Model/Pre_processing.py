import numpy as np                      # For numerical operations
import pandas as pd                     # For handling DataFrames
from sklearn.model_selection import train_test_split  # For splitting datasets
from sklearn.preprocessing import OneHotEncoder      # For one-hot encoding labels
import joblib

class DataPreparator:
    def __init__(self, emotion_data, features, test_size=0.3, random_state=42):
        self.emotion_data = emotion_data
        self.features = features
        self.test_size = test_size
        self.random_state = random_state
        self.encoder = OneHotEncoder()

    def encode_labels(self):
        # One-hot encode the emotion labels
        self.y = self.emotion_data['emotions'].to_numpy().reshape(-1, 1)
        self.y_encoded = self.encoder.fit_transform(self.y).toarray()
        print(f"Encoded class labels: {self.encoder.get_feature_names_out()}")
        print(f"Shape of y_encoded: {self.y_encoded.shape}")
                # Save the encoder to a file for future use
        joblib.dump(self.encoder, 'Model/encoder.pkl')
        print("Encoder saved to 'encoder.pkl'.")

        return self.y_encoded

    def split_data(self):
        # Split the data into train, validation, and test sets
        X = pd.DataFrame(self.features)
        y = self.y_encoded

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, shuffle=True)

        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")

        return X_train, X_test, y_train, y_test
