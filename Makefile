.PHONY: setup_env

setup_env:
	python3 -m venv .venv_qt_uart_control_center
	source .venv_qt_uart_control_center/bin/activate
	pip install -r requirements.txt