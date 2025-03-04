import os
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

from utils import generate_timestamp


class SerialWorker(QObject):
    """
    Worker thread for handling serial communication.
    """
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serial = QSerialPort()
        self.serial.readyRead.connect(self.read_data)
        self.baudrate = 115200  # WARNING: Default baudrate. Can be changes, but if always the same, specify it here
        self.log_filename = None

    def list_ports(self):
        ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        return ports

    def connect_serial(self, port):
        if self.serial.isOpen():
            self.serial.close()

        self.serial.setPortName(port)
        self.serial.setBaudRate(self.baudrate)

        if self.serial.open(QSerialPort.OpenModeFlag.ReadWrite):
            self.data_received.emit(f"Connected to {port}")
            self.create_log_file()
        else:
            self.error_occurred.emit(f"Failed to connect to {port}")

    def disconnect_serial(self):
        if self.serial.isOpen():
            self.serial.close()
            self.log_filename = None
            self.data_received.emit("Disconnected from serial device.")

    def create_log_file(self):
        """
        Logfile will be saved as 'log_PORT_TIMESTAMP.txt', where:
            - PORT is the comm port connected, replacing OS-specific filesystem separator with '-'
            - TIMESTAMP has the format YYYY-mm-dd-HH-MM-SS
        """
        self.log_filename = f'log_{self.port.replace(os.path.sep, '-')}_{generate_timestamp()}.txt'
        with open(f'logs/{self.log_filename}', "w+") as f:
            pass

    def log_line(self, data: str, is_read: bool = True):
        prefix = "RX" if is_read else "TX"
        if self.log_filename is not None:
            with open(f'logs/{self.log_filename}', "a") as f:
                new_log_line = prefix + "->" + data + "\n"  # WARNING: Check if your received data has already a newline byte
                f.write(new_log_line)

    
    # WARNING: Maybe you need to wrap the read .decode() around a try - except (DecodeError) to avoid crash if undecodeable byte received
    def read_data(self):
        while self.serial.canReadLine():
            data = self.serial.readLine().data().decode().strip()
            self.log_line(data=data, is_read=True)
            self.data_received.emit(data)

    def send_data(self, message):
        if self.serial.isOpen():
            self.log_line(data=message, is_read=False)
            self.serial.write((message + "\n").encode())
