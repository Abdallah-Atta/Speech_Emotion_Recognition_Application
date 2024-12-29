import os
import pandas as pd

class SpeechEmotionData:
    def __init__(self, rav_path, tess_path):
        self.rav_path = rav_path
        self.tess_path = tess_path

    def get_rav_data(self):
        label_map_ravdess = {
            '01': 'neutral', '02': 'calm', '03': 'happy', '04': 'sad',
            '05': 'angry', '06': 'fearful', '07': 'disgust', '08': 'surprised'
        }
        ravdess_file_paths = []
        ravdess_labels = []

        for actor in os.listdir(self.rav_path):
            # Ensure the folder represents an actor
            if actor.startswith('A'):
                actor_path = os.path.join(self.rav_path, actor)

                # Loop through each audio file for the actor
                for file in os.listdir(actor_path):
                    if file.startswith('0'):
                        file_path = os.path.join(actor_path, file)
                        # Store the file path
                        ravdess_file_paths.append(file_path)
                        # Extract the emotion code from the filename
                        emotion = file[6:8]
                        # Map the emotion code to a label
                        ravdess_labels.append(label_map_ravdess[emotion])

        # Create a pandas DataFrame
        rav_data = pd.DataFrame({
            'paths': ravdess_file_paths,
            'emotions': ravdess_labels
        })
        rav_data.to_csv("Model/rav_data.csv", index=False)
        return rav_data

    def get_tess_data(self):
        self.tess_path = os.path.join(self.tess_path,'TESS Toronto emotional speech set data')
        tess_file_paths = []
        tess_labels = []

        for folder in os.listdir(self.tess_path):
            if folder.startswith('O') or folder.startswith('Y'):
                folder_path = os.path.join(self.tess_path, folder)

                # Extract emotion label from the folder name (e.g., 'OAF_Fear' -> 'fear')
                label = folder[4:].lower()

                # Loop through each file in the folder
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    # Store the file path
                    tess_file_paths.append(file_path)
                    # Store the corresponding emotion label
                    tess_labels.append(label)

        # Create a DataFrame
        tess_data = pd.DataFrame({
            'paths': tess_file_paths,
            'emotions': tess_labels
        })

        # Standardize emotion labels
        tess_data['emotions'] = tess_data['emotions'].replace({
            'pleasant_surprise': 'surprised',
            'pleasant_surprised': 'surprised',
            'fear': 'fearful',
            'disguist' : 'disgust'
        })
        tess_data.to_csv("Model/tess_data.csv", index=False)
        return tess_data

    def combine_data(self):
        # Get RAVDESS and TESS data
        rav_data = self.get_rav_data()
        tess_data = self.get_tess_data()

        # Combine both datasets
        emotion_data = pd.concat([rav_data, tess_data], axis=0).reset_index(drop=True)

        return emotion_data


