import numpy as np                          # For numerical operations
import pandas as pd                        # For handling data frames
import librosa                             # For audio processing
import soundfile as sf                     # For writing augmented audio data


class AudioAugmentor:
    def __init__(self, emotion_data, noise_factor=0.005, pitch_factor=None, max_neutral_samples=592, max_calm_samples=592):
        self.emotion_data = emotion_data
        self.noise_factor = noise_factor
        self.pitch_factor = pitch_factor or np.random.uniform(-5, 5)
        self.max_neutral_samples = max_neutral_samples
        self.max_calm_samples = max_calm_samples
        self.nof_neutral_samples = emotion_data['emotions'].value_counts().get('neutral', 0)
        self.nof_calm_samples = emotion_data['emotions'].value_counts().get('calm', 0)

    def add_noise(self, data):
        """Add random noise to the audio data."""
        noise = np.random.randn(len(data)) * self.noise_factor
        return data + noise

    def pitch_shift(self, data, sample_rate):
        """Apply pitch shifting to the audio data."""
        return librosa.effects.pitch_shift(data, sr=sample_rate, n_steps=self.pitch_factor)

    def augment_data(self):
        """Augment audio data by adding noise and pitch shifting."""
        augmented_paths = []
        augmented_emotions = []
        neutral_count = 0  # Track the number of augmented 'neutral' samples
        calm_count = 0     # Track the number of augmented 'calm' samples

        for index, row in self.emotion_data.iterrows():
            path = row['paths']
            emotion = row['emotions']
            data, sample_rate = librosa.load(path, sr=None)

            # Augment 'neutral' emotion
            if emotion == 'neutral' and neutral_count < (self.max_neutral_samples - self.nof_neutral_samples):
                noisy_data = self.add_noise(data)
                noisy_path = path.replace('.wav', '_noise.wav')
                sf.write(noisy_path, noisy_data, sample_rate)
                augmented_paths.append(noisy_path)
                augmented_emotions.append(emotion)
                neutral_count += 1
                print('neutral_count:', neutral_count)

            # Augment 'calm' emotion
            elif emotion == 'calm' and calm_count < (self.max_calm_samples - self.nof_calm_samples):
                noisy_data = self.add_noise(data)
                noisy_path = path.replace('.wav', '_noise.wav')
                sf.write(noisy_path, noisy_data, sample_rate)
                augmented_paths.append(noisy_path)
                augmented_emotions.append(emotion)
                calm_count += 1
                print('calm_count:', calm_count)

                # Apply pitch shift to 'calm' data
                pitch_data = self.pitch_shift(data, sample_rate)
                pitch_path = path.replace('.wav', '_pitch.wav')
                sf.write(pitch_path, pitch_data, sample_rate)
                augmented_paths.append(pitch_path)
                augmented_emotions.append(emotion)
                calm_count += 1
                print('calm_count:', calm_count)

        augmented_data = pd.DataFrame({
            'paths': augmented_paths,
            'emotions': augmented_emotions
        })

        combined_data = pd.concat([self.emotion_data, augmented_data], ignore_index=True)
        return combined_data