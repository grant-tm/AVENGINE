import librosa

class AudioEngine:
    
    def __init__(self):
        # data
        self.sample_rate = None
        self.audio_wave = None
        self.audio_spectrum = None
        
        # operating parameters
        self.play_status = False
    
    def load_audio(self, file_path):
        data, sr = librosa.load(file_path, sr=None)
        self.sample_rate = sr
        self.original_waveform = data
        return data, sr