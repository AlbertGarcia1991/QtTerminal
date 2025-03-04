import cv2
import numpy as np
import os
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QGridLayout,
    QComboBox, QLabel, QVBoxLayout
)

from utils import generate_timestamp


class ControlPanelWindow(QWidget):
    """
    Control panel window with 6 buttons, each sending predefined commands.
    """
    def __init__(self, terminal_window):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.setGeometry(100, 100, 300, 300)
        self.terminal_window = terminal_window

        self.layout = QVBoxLayout()

        # Webcam Selection Dropdown
        self.camera_label = QLabel("Select Camera:")
        self.layout.addWidget(self.camera_label)

        self.camera_dropdown = QComboBox()
        self.layout.addWidget(self.camera_dropdown)


        # Start/Stop Recording Button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setEnabled(False)  # Disabled until a camera is selected
        self.record_button.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.record_button)

        # Camera Setup
        self.cap = None
        self.is_recording = False
        self.video_writer = None

        # Timer to continuously grab frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)

        # Buttons Grid Layout (2x3)
        self.button_layout = QGridLayout()
        self.commands = ["CMD_1", "CMD_2", "CMD_3", "CMD_4", "CMD_5", "CMD_6"]
        self.buttons = []

        self.init_ui()
        self.refresh_camera_list()

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # Enable recording button when camera is selected
        self.camera_dropdown.currentIndexChanged.connect(self.enable_recording_button)

    def init_ui(self):
        for i in range(6):
            button = QPushButton(f"Button {i + 1}")
            button.clicked.connect(lambda _, cmd=self.commands[i]: self.send_command(cmd))
            self.buttons.append(button)
            self.button_layout.addWidget(button, i // 2, i % 2)

    def send_command(self, command):
        self.terminal_window.update_terminal(f"> {command}")
        self.terminal_window.send_command_signal.emit(command)

    def refresh_camera_list(self):
        """Detects available cameras and populates the dropdown."""
        self.camera_dropdown.clear()
        available_cameras = self.detect_available_cameras()
        self.camera_dropdown.addItems(available_cameras)

        # Enable the record button if at least one camera is available
        self.record_button.setEnabled(len(available_cameras) > 0)

    def detect_available_cameras(self):
        """Detects available camera indices by trying to open them."""
        available_cameras = []
        for index in range(5):  # Check up to 5 camera indices
            cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
            if cap.isOpened():
                available_cameras.append(f"Camera {index}")
                cap.release()
        return available_cameras

    def enable_recording_button(self):
        """Enable Start/Stop button if a camera is selected."""
        self.record_button.setEnabled(self.camera_dropdown.count() > 0)

    def toggle_recording(self):
        """Starts or stops recording based on the current state."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        # WARNING: Not sure about the video recording (if it is working..), maybe you need to double check it!
        """Starts video capture and recording."""
        selected_camera_index = self.camera_dropdown.currentIndex()
        if selected_camera_index == -1:
            return

        self.cap = cv2.VideoCapture(selected_camera_index, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            self.terminal_window.update_terminal("Failed to open the selected camera.")
            return

        # Get frame width and height
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 20  # Frames per second

        # Generate filename with timestamp
        timestamp = generate_timestamp()
        if not os.path.isdir('videos'):
            os.makedirs('videos')
        self.video_filename = os.path.join("videos", f"recording_{timestamp}.avi")

        # Define codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, fps, (frame_width, frame_height))

        self.is_recording = True
        self.record_button.setText("Stop Recording")

        # Start capturing frames every 50 ms (~20 FPS)
        self.timer.start(50)

        self.terminal_window.update_terminal(f"Recording started: {self.video_filename}")

    def capture_frame(self):
        """Captures frames from the camera and writes them to the video file."""
        if self.cap is None or not self.cap.isOpened() or self.video_writer is None:
            return

        ret, frame = self.cap.read()
        if ret:
            self.video_writer.write(frame)

    def stop_recording(self):
        """Stops video capture and saves the recording."""
        self.timer.stop()  # Stop frame capture

        if self.cap:
            self.cap.release()
            self.cap = None

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.is_recording = False
        self.record_button.setText("Start Recording")

        self.terminal_window.update_terminal(f"Recording saved as: {self.video_filename}")

    def closeEvent(self, event):
        """Closes both windows and releases the camera if recording."""
        if self.is_recording:
            self.stop_recording()
        self.terminal_window.close()  # Close the Terminal
        event.accept()
