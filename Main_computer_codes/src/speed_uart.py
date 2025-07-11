def setup_uart():
    """Initialize UART connection"""
    try:
        uart = serial.Serial(
            port=UART_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT
        )
        return uart
    except Exception as e:
        print(f"UART initialization failed: {e}")
        return None

def send_speeds(uart, m1, m2, m3):
    """Send motor speeds to Pico"""
    try:
        command = f"{m1:.2f},{m2:.2f},{m3:.2f}\n"
        uart.write(command.encode('utf-8'))
        print(f"Sent: {command.strip()}")
    except Exception as e:
        print(f"Error sending speeds: {e}")

def receive_speeds(uart):
    """Receive actual speeds from Pico"""
    try:
        if uart.in_waiting > 0:
            response = uart.readline().decode('utf-8').strip()
            print(f"Received: {response}")
            return response
        return None
    except Exception as e:
        print(f"Error receiving speeds: {e}")
        return None