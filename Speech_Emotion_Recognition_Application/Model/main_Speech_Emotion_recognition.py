from get_data import SpeechEmotionData
from Exploration_data import EmotionDataExploration
from Data_Augumentation import AudioAugmentor
from Features_Extraction import FeatureExtractor
from Pre_processing import DataPreparator
from Model_build import train_cnn_model
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub
import joblib
import numpy as np
import pandas as pd

# ---------------------------------- Get & Combine Datasets ----------------------------------

rav_path = kagglehub.dataset_download("uwrfkaggler/ravdess-emotional-speech-audio")
tess_path = kagglehub.dataset_download("ejlok1/toronto-emotional-speech-set-tess")

# Create an instance of the class
speech_data = SpeechEmotionData(rav_path, tess_path)

# Combine data and check integrity
emotion_data = speech_data.combine_data()

print('Get & Combine Datasets')

# ---------------------------------- Explore Dataset ----------------------------------

emotion_processor = EmotionDataExploration(emotion_data=emotion_data)
emotion_processor.process_emotions()

print('Explore Dataset')

# ---------------------------------- Data_Augmentor ----------------------------------

plt.figure(figsize=(10,6))
sns.countplot(data=emotion_data, x='emotions')
plt.title("Before_Augmentor")
plt.savefig("Model/Before_Augmentor.png")
plt.close()

augmentor = AudioAugmentor(emotion_data)

emotion_data = augmentor.augment_data()

plt.figure(figsize=(10,6))
sns.countplot(data=emotion_data, x='emotions')
plt.title("After_Augmentor")
plt.savefig("Model/After_Augmentor.png")
plt.close()

print('Pre_processing Dataset')

# ---------------------------------- Feature_Extraction Dataset ----------------------------------

extractor = FeatureExtractor(emotion_data=emotion_data)
extractor.extract_features()
extractor.combine_features()
features = extractor.normalize_features()

print('Feature_Extraction Dataset')

# ---------------------------------- Pre_Paration ----------------------------------

preparator = DataPreparator(emotion_data=emotion_data, features=features)
y_encoded = preparator.encode_labels()
X_train, X_test, y_train, y_test = preparator.split_data()

print("Train,and Test sets are ready for use.")

# ---------------------------------- Model ----------------------------------

history, trained_model = train_cnn_model(X_train, y_train, X_test, y_test)

# Plot training and validation accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Train vs Val Accuracy for CNN')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'])
plt.savefig("Model/Train_vs_Val_Accuracy_for_CNN.png")
plt.close()

# lets plot the loss (both training and validation) vs epochs

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('train vs val loss for CNN')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'])
plt.savefig("Model/train_vs_val_loss_for_CNN.png")
plt.close()


# Save the model
trained_model.save('Model/speech_emotion_cnn_model.h5')
trained_model.save('Model/speech_emotion_cnn_model.keras')
print("Model saved as 'speech_emotion_cnn_model.h5'")

# ---------------------------------- Confusion_Matrix ----------------------------------

# Step 1: Make predictions on X_test
y_pred = trained_model.predict(X_test)  # Use the model's .predict() method

# Assuming you have a classification model, and the output needs to be converted to predicted class labels
predicted_labels = np.argmax(y_pred, axis=1)

# Convert y_test from one-hot encoding to class labels
y_test_labels = np.argmax(y_test, axis=1)

# Step 2: Generate confusion matrix
conf_matrix = confusion_matrix(y_test_labels, predicted_labels)

# Define class labels based on your provided classes
encoder = joblib.load("Model/encoder.pkl")
encoded_labels = encoder.get_feature_names_out().tolist()
cleaned_labels = [label.replace('x0_', '') for label in encoded_labels]
# Step 3: Plot confusion matrix using seaborn for better visualization
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=cleaned_labels, yticklabels=cleaned_labels)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.savefig("Model/Confusion_Matrix.png")

# ---------------------------------- classification_report ----------------------------------

# Assuming you have already converted y_test and y_pred_class to class labels
y_test_class = np.argmax(y_test, axis=1)  # Convert y_test to class labels if it's one-hot encoded
y_pred_class = np.argmax(y_pred, axis=1)  # Convert predicted probabilities to class labels

# Generate classification report
report = classification_report(y_test_class, y_pred_class, output_dict=True)

# Convert the classification report dictionary to a DataFrame for plotting
report_df = pd.DataFrame(report).iloc[:-1, :].T  # Drop the 'accuracy' row

# Plot the heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(report_df, annot=True, cmap="Blues", fmt=".2f", cbar=True)
plt.title("Classification Report Heatmap")
plt.savefig("Model/Classification_Report_Heatmap.png")