from PyQt6.QtWidgets import (
    QWidget, QPushButton, QGridLayout,
)


class ControlPanelWindow(QWidget):
    """
    Control panel window with 6 buttons, each sending predefined commands.
    """
    def __init__(self, terminal_window):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.setGeometry(100, 100, 300, 300)
        self.terminal_window = terminal_window

        self.layout = QGridLayout()

        self.buttons = []

        self.commands = [
            "CMD_1",
            "CMD_2",
            "CMD_3",
            "CMD_4",
            "CMD_5",
            "CMD_6"
        ]

        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        for i in range(6):
            button = QPushButton(f"Button {i + 1}")
            button.clicked.connect(lambda _, cmd=self.commands[i]: self.send_command(cmd))
            self.buttons.append(button)
            self.layout.addWidget(button, i // 2, i % 2)

    def send_command(self, command):
        self.terminal_window.update_terminal(f"> {command}")
        self.terminal_window.send_command_signal.emit(command)

    def closeEvent(self, event):
        self.terminal_window.close()  # Close the Terminal
        event.accept()
