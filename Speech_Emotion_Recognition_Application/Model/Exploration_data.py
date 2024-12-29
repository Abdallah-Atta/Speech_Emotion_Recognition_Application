import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf  # To save the audio file
from IPython.display import Audio

class EmotionDataExploration:
    def __init__(self, emotion_data, base_dir='image_and_audio'):
        self.emotion_data = emotion_data
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def waveplot(self, data, sr, emotion, save_path):
        plt.figure(figsize=(10, 4))
        plt.title(emotion, size=20)
        librosa.display.waveshow(data, sr=sr)
        plt.savefig(save_path)
        plt.close()

    def spectogram(self, data, sr, emotion, save_path):
        x = librosa.stft(data)
        xdb = librosa.amplitude_to_db(abs(x))
        plt.figure(figsize=(11, 4))
        plt.title(emotion, size=20)
        librosa.display.specshow(xdb, sr=sr, x_axis='time', y_axis='hz')
        plt.colorbar()
        plt.savefig(save_path)
        plt.close()

    def process_emotions(self, emotions=None):
        if emotions is None:
            emotions = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']

        # Loop through each emotion
        for emotion in emotions:
            # Get the file path for one sample of this emotion
            path = np.array(self.emotion_data['paths'][self.emotion_data['emotions'] == emotion])[0]
            data, sampling_rate = librosa.load(path)

            # Create a directory for each emotion under the base folder
            emotion_dir = os.path.join(self.base_dir, emotion)
            os.makedirs(emotion_dir, exist_ok=True)

            # Generate and save the waveform plot
            waveplot_save_path = os.path.join(emotion_dir, f"{emotion}_waveplot.png")
            self.waveplot(data, sampling_rate, emotion, waveplot_save_path)

            # Generate and save the spectrogram plot
            spectrogram_save_path = os.path.join(emotion_dir, f"{emotion}_spectrogram.png")
            self.spectogram(data, sampling_rate, emotion, spectrogram_save_path)

            # Save the audio file in the same emotion directory
            audio_save_path = os.path.join(emotion_dir, f"{emotion}.wav")
            sf.write(audio_save_path, data, sampling_rate)

            # Optionally, play the audio (for Jupyter environments)
            Audio(path)

        print(f"All emotion data (images and audio) are saved in '{self.base_dir}' directory.")



# image_and_audio/
#     ├── neutral/
#     │   ├── neutral_waveplot.png
#     │   ├── neutral_spectrogram.png
#     │   ├── neutral.wav
#     ├── calm/
#     │   ├── calm_waveplot.png
#     │   ├── calm_spectrogram.png
#     │   ├── calm.wav
#     ├── happy/
#     │   ├── happy_waveplot.png
#     │   ├── happy_spectrogram.png
#     │   ├── happy.wav
#     ...
