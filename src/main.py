import os
from PyQt6.QtWidgets import QApplication
import sys

from window_control_panel import ControlPanelWindow
from window_terminal import TerminalWindow


class MainApplication:
    """
    Main application to run both windows in parallel.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.create_log_folder()

        self.terminal_window = TerminalWindow()
        self.control_panel_window = ControlPanelWindow(self.terminal_window)
        self.terminal_window.control_panel_window = self.control_panel_window

        self.terminal_window.show()
        self.control_panel_window.show()

    def create_log_folder(self):
        if not os.path.isdir('logs'):
            os.makedirs('logs')

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = MainApplication()
    app.run()