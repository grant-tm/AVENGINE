import librosa
import numpy as np
import pyqtgraph as pg
from pyqtgraph import ColorMap

MAX_VISIBLE_POINTS = 50000

class WaveDisplay:
    
    # Init function
    #---------------------------------------------------------------------------
    def __init__(self, plot_widget):
        
        # plot widget
        self.plot_widget = plot_widget
        self.plot_widget.setYRange(-1, 1)
        self.plot_widget.setMouseEnabled(y=False)
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        
        # view box
        self.view_box = self.plot_widget.getViewBox()
        self.view_box.sigRangeChanged.connect(self.dynamic_downsample)
        
        # store audio context
        self.sample_rate = None
        self.scale_factor = 1.0
        
        # store audio
        self.raw_waveform = None
        self.raw_times = None
        
        # modifiable variables
        self.display_waveform = None
        self.display_times = None

    # Set the raw waveform that the display is based on
    #---------------------------------------------------------------------------
    def set_wave(self, waveform, sample_rate):
        self.sample_rate = sample_rate

        self.raw_waveform = waveform
        self.raw_times = np.linspace(0, len(self.raw_waveform) / sample_rate, num=len(self.raw_waveform))
        self.view_box.setLimits(xMin=self.raw_times[0], xMax=self.raw_times[-1])
        
        self.display_waveform = self.raw_waveform
        self.display_times = np.linspace(0, len(self.display_waveform) / sample_rate, num=len(self.raw_waveform))
        
        self.render()

    # Dynamically downsample the waveform based on zoom level
    #---------------------------------------------------------------------------
    def dynamic_downsample(self, view_box, view_range):
        x_range, _ = view_range  # Extract the X range (time) from the view
        x_min, x_max = x_range  # Get the minimum and maximum X values currently in view

        # Find the indices corresponding to the visible range
        visible_indices = np.where((self.raw_times >= x_min) & (self.raw_times <= x_max))[0]
        if len(visible_indices) <= 0:
            return

        # Extract visible portion of the original waveform
        original_start_idx = visible_indices[0]
        original_end_idx = visible_indices[-1]
        visible_waveform = self.raw_waveform[original_start_idx:original_end_idx]

        # Downsample to at most MAX_VISIBLE_POINTS points
        max_points = MAX_VISIBLE_POINTS
        if len(visible_waveform) > max_points:
            downsample_factor = len(visible_waveform) // max_points
            # Ensure the downsample factor is at least 1
            downsample_factor = max(1, downsample_factor)
            downsampled_waveform = visible_waveform[::downsample_factor]
        else:
            downsampled_waveform = visible_waveform

        # Trigger re-render if significant change in number of points
        self.display_waveform = downsampled_waveform
        self.display_times = np.linspace(x_min, x_max, num=len(downsampled_waveform))
        self.render()
        
    # Plot the display waveform on the graph widget
    #---------------------------------------------------------------------------
    def render(self):
        print(len(self.display_waveform))
        self.plot_widget.clear()
        self.plot_widget.plot(self.display_times, self.display_waveform * self.scale_factor)
    
    # Update the scale factor
    #---------------------------------------------------------------------------
    def set_scale_factor(self, scaling_factor):
        self.scale_factor = scaling_factor
        self.render()
        