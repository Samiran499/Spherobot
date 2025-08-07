import serial

def setup_uart(uart_port="/dev/serial0", baud_rate=115200, timeout=1):
    """Initialize UART connection"""
    try:
        uart = serial.Serial(
            port=uart_port,
            baudrate=baud_rate,
            timeout=timeout
        )
        print(f"UART initialized on {uart_port} at {baud_rate} baud")
        return uart
    except Exception as e:
        print(f"UART initialization failed: {e}")
        return None

def send_speeds(uart, m1, m2, m3, debug=False):
    """Send motor speeds to Pico"""
    try:
        command = f"{m1:.2f},{m2:.2f},{m3:.2f}\n"
        uart.write(command.encode('utf-8'))
        uart.flush()  # Ensure data is sent immediately
        if debug:
            print(f"Sent: {command.strip()}")
        return True
    except Exception as e:
        print(f"Error sending speeds: {e}")
        return False

def receive_speeds(uart, debug=False):
    """
    Placeholder function for future implementation
    Currently not used as per requirements
    """
    # This function is kept for future use but currently does nothing
    # as receiving speeds from Pico is not needed right now
    pass

def check_uart_connection(uart):
    """Check if UART connection is still active"""
    try:
        return uart.is_open
    except Exception:
        return False

def close_uart(uart):
    """Safely close UART connection"""
    try:
        if uart and uart.is_open:
            uart.close()
            print("UART connection closed")
    except Exception as e:
        print(f"Error closing UART: {e}")