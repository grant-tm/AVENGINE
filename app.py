import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDial, QLabel, QHBoxLayout, QFileDialog
import pyqtgraph as pg
from wave_display import WaveDisplay
from audio_engine import AudioEngine

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("AVEngine")
        self.setGeometry(100, 100, 1000, 800)

        # Layout setup
        self.main_layout = QVBoxLayout()
        self.widget = QWidget(self)
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

        # Audio Engine
        self.audio_engine = AudioEngine()
        
        # Wave Display
        self.wave_plot = pg.PlotWidget(title="Waveform")
        self.wave_display = WaveDisplay(self.wave_plot)
        
        # File load button
        self.load_button = QPushButton('Load Audio', self)
        self.load_button.clicked.connect(self.load_audio)
        self.main_layout.addWidget(self.load_button)

        # Horizontal layout for dial and label
        self.dial_layout = QHBoxLayout()
        self.main_layout.addLayout(self.dial_layout)

        # Amplitude scaling label and dial
        self.amplitude_label = QLabel('Amplitude Scaling: 1.0', self)
        self.dial_layout.addWidget(self.amplitude_label)

        self.amplitude_dial = QDial(self)
        self.amplitude_dial.setRange(1, 20)
        self.amplitude_dial.setValue(10)
        self.amplitude_dial.valueChanged.connect(self.update_amplitude_scaling)
        self.dial_layout.addWidget(self.amplitude_dial)

        # Add waveform plot to layout
        self.main_layout.addWidget(self.wave_plot)

    def load_audio(self):
        file_dialog = QFileDialog()
        audio_file, _ = file_dialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3)")
        
        if audio_file:
            waveform, sample_rate = self.audio_engine.load_audio(audio_file)
            self.wave_display.set_wave(waveform, sample_rate)

    def update_amplitude_scaling(self):
        scaling_factor = self.amplitude_dial.value() / 10.0
        self.amplitude_label.setText(f'Amplitude Scaling: {scaling_factor:.1f}')

        #if self.audio_engine.original_waveform is not None:
            #downsampled_waveform, times = self.audio_engine.get_downsampled_waveform(max_points=25000)
            #self.wave_display.update_waveform_plot(downsampled_waveform, times, scaling_factor)

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec_())
