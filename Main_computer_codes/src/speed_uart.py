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
    """Receive actual speeds from Pico"""
    try:
        if uart.in_waiting > 0:
            response = uart.readline().decode('utf-8').strip()
            if response:  # Only print non-empty responses
                if debug:
                    print(f"Received: {response}")
                # Parse the response to get actual motor speeds
                try:
                    speeds = [float(x) for x in response.split(',')]
                    if len(speeds) == 3:
                        return speeds
                    else:
                        if debug:
                            print(f"Warning: Expected 3 speeds, got {len(speeds)}")
                except ValueError:
                    if debug:
                        print(f"Warning: Could not parse speeds from: {response}")
            return response
        return None
    except Exception as e:
        print(f"Error receiving speeds: {e}")
        return None

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