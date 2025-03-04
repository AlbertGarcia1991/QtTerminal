from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QLineEdit,
)

from serial_worker import SerialWorker


class TerminalWindow(QWidget):
    """
    Terminal window that allows user to send and receive serial data.
    """
    send_command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terminal")
        self.setGeometry(600, 100, 500, 400)
        self.control_panel_window = None
        
        self.layout = QVBoxLayout()

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.layout.addWidget(self.terminal_output)

        self.input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_command)
        self.input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("SEND")
        self.send_button.clicked.connect(self.send_command)
        self.input_layout.addWidget(self.send_button)

        self.layout.addLayout(self.input_layout)
        self.setLayout(self.layout)

        self.serial_worker = SerialWorker()
        self.serial_worker.data_received.connect(self.update_terminal)
        self.serial_worker.error_occurred.connect(self.update_terminal)
        
        self.send_command_signal.connect(self.serial_worker.send_data)

    def send_command(self):
        command = self.input_field.text().strip()
        if not command:
            return

        self.update_terminal(f"> {command}")
        self.input_field.clear()

        # WARNING: Special commands in case you need them. You can add/remove/hack the code
        if command == "/devices":
            ports = self.serial_worker.list_ports()
            self.update_terminal("Available ports:\n" + "\n".join(ports))
        elif command == "/baud":
            args = command.split()
            if len(args) != 2:
                self.update_terminal(f"You need to specify the BAUDRATE")
            else:
                self.serial_worker.baudrate = int(args[1])
        elif command == command.startswith("/connect"):
            args = command.split()
            if len(args) != 2:
                self.update_terminal(f"You need to specify the PORT to connect")
            else:
                self.serial_worker.connect_serial(args[1])
        elif command == "/disconnect":
            self.serial_worker.disconnect_serial()
        elif command == "/help":
            self.update_terminal(f"Available commands:")
            self.update_terminal(f"\t /devices: print connected serial devices")
            self.update_terminal(f"\t /baud BAUDRATE: change baudrate to given by BAUDRATE")
            self.update_terminal(f"\t /connect PORT: open serial connection with PORT device")
            self.update_terminal(f"\t /disconnect: disconnect current serial connection")
        else:
            self.serial_worker.send_data(command)

    def update_terminal(self, message):
        self.terminal_output.append(message)

    def closeEvent(self, event):
        self.control_panel_window.close()  # Close the Control Panel
        event.accept()