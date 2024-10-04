import sys
import librosa
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QDial, QLabel, QHBoxLayout

MAX_VISIBLE_POINTS = 25000

class AudioWaveformApp(QMainWindow):
    def __init__(self):
        super().__init__()        
        
        # Set up the main window
        self.setWindowTitle("AVEngine")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        self.main_layout = QVBoxLayout()
        self.widget = QWidget(self)
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

        # Button to load audio
        self.load_button = QPushButton('Load Audio', self)
        self.load_button.clicked.connect(self.load_audio)
        self.main_layout.addWidget(self.load_button)

        # Horizontal layout for dial and label
        self.dial_layout = QHBoxLayout()
        self.main_layout.addLayout(self.dial_layout)

        # Label to display amplitude scaling value
        self.amplitude_label = QLabel('Amplitude Scaling: 1.0', self)
        self.dial_layout.addWidget(self.amplitude_label)

        # QDial for controlling the amplitude scaling
        self.amplitude_dial = QDial(self)
        self.amplitude_dial.setRange(1, 20)  # Scaling factor from 0.1 to 2.0 (adjustable)
        self.amplitude_dial.setValue(10)  # Default value (1.0 scaling)
        self.amplitude_dial.valueChanged.connect(self.update_amplitude_scaling)
        self.dial_layout.addWidget(self.amplitude_dial)

        # PyQtGraph Plot for the waveform
        self.waveform_plot = pg.PlotWidget(title="Waveform")
        self.main_layout.addWidget(self.waveform_plot)

        # Fix the vertical range (amplitude)
        self.waveform_plot.setYRange(-1, 1)  # Assuming normalized amplitude between -1 and 1
        self.waveform_plot.setMouseEnabled(y=False)  # Disable vertical zooming
        self.waveform_plot.setLabel('left', 'Amplitude')
        self.waveform_plot.setLabel('bottom', 'Time', units='s')

        # Access the ViewBox to set limits later
        self.view_box = self.waveform_plot.getViewBox()
        
        # Connect the zoom level change signal to a custom method
        self.view_box.sigRangeChanged.connect(self.on_zoom_change)

        # Placeholder for the waveform data
        self.sample_rate = None
        self.original_waveform = None
        self.downsampled_waveform = None
        self.downsample_factor = 1
        self.times_downsampled = None
        self.amplitude_scaling_factor = 1.0

    def load_audio(self):
        # Open file dialog to select audio file
        file_dialog = QFileDialog()
        audio_file, _ = file_dialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3)")

        # Load audio file using librosa
        if audio_file:
            self.plot_waveform(audio_file)

    def plot_waveform(self, audio_file):
        # Load the audio file and extract the waveform and sample rate
        data, sr = librosa.load(audio_file, sr=None)

        # Downsample the waveform data for faster plotting
        max_points = MAX_VISIBLE_POINTS  # Maximum number of points to plot (adjust as needed)
        downsample_factor = max(1, len(data) // max_points)
        self.sample_rate = sr
        self.original_waveform = data
        self.downsampled_waveform = data[::downsample_factor]
        self.times_downsampled = np.linspace(0, len(data) / sr, num=len(self.original_waveform))

        # Plot the waveform with the current amplitude scaling factor
        self.update_waveform_plot()

        # Set X-axis limits to prevent scrolling past the waveform
        self.view_box.setLimits(xMin=self.times_downsampled[0], xMax=self.times_downsampled[-1])

    def update_waveform_plot(self):
        """ Update the plot based on the current amplitude scaling factor. """
        if self.original_waveform is not None and self.times_downsampled is not None:
            # Apply the amplitude scaling
            scaled_waveform = self.original_waveform * self.amplitude_scaling_factor

            # Plot the downsampled and scaled waveform
            self.waveform_plot.clear()
            self.waveform_plot.plot(self.times_downsampled, scaled_waveform, pen='b')

            # The Y-range stays constant, so we don't change it here

    def update_amplitude_scaling(self):
        """ Update the amplitude scaling factor when the dial is changed. """
        dial_value = self.amplitude_dial.value()
        self.amplitude_scaling_factor = dial_value / 10.0  # Convert dial value to scaling factor (0.1 to 2.0)

        # Update label text to show current scaling
        self.amplitude_label.setText(f'Amplitude Scaling: {self.amplitude_scaling_factor:.1f}')

        # Update the waveform plot with the new amplitude scaling factor
        self.update_waveform_plot()

    def on_zoom_change(self, view_box, view_range):
        """Regenerate the visible waveform with 10,000 points based on the current zoom level."""
        x_range, _ = view_range  # Extract the X range (time) from the view
        x_min, x_max = x_range  # Get the minimum and maximum X values currently in view

        # Find the indices corresponding to the visible range in self.times_downsampled
        visible_indices = np.where((self.times_downsampled >= x_min) & (self.times_downsampled <= x_max))[0]
        if len(visible_indices) <= 0:
            return
        
        # Extract visible portion of the original waveform
        original_start_idx = visible_indices[0]# * self.downsample_factor
        original_end_idx = visible_indices[-1]# * self.downsample_factor
        visible_waveform = self.original_waveform[original_start_idx:original_end_idx]

        # Downsample to at most 10,000 points
        max_points = MAX_VISIBLE_POINTS
        if len(visible_waveform) > max_points:
            downsample_factor = len(visible_waveform) // max_points
            downsampled_waveform = visible_waveform[::downsample_factor]
        else:
            downsampled_waveform = visible_waveform

        # Create the corresponding time axis for the downsampled waveform
        visible_times = np.linspace(x_min, x_max, num=len(downsampled_waveform))

        # Update the plot with the new downsampled waveform
        self.waveform_plot.clear()
        self.waveform_plot.plot(visible_times, downsampled_waveform, pen='b')
        

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioWaveformApp()
    window.show()
    sys.exit(app.exec_())
