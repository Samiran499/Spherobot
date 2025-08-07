import csv
import requests
import serial
import time
from src.kinematics_mapping import map_speed
from src.speed_uart import setup_uart, send_speeds, receive_speeds, check_uart_connection, close_uart

# UART Configuration
UART_PORT = "/dev/serial0"  # Default UART port on Pi Zero
BAUD_RATE = 115200
TIMEOUT = 1

buffer = []
log_interval = 100  # How many samples before writing to CSV
debug_mode = True  # Set to False to reduce console output

def main():
    print("Starting Spherobot Main Computer...")
    print(f"UART Port: {UART_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    
    uart = setup_uart(UART_PORT, BAUD_RATE, TIMEOUT)
    if uart is None:
        print("Failed to initialize UART. Exiting...")
        return

    print("Waiting for Pico to be ready...")
    time.sleep(2)  # Give Pico time to start up
    
    # Send a test command to verify connection
    print("Testing UART connection...")
    if send_speeds(uart, 0, 0, 0, True):
        print("UART connection test successful")
    else:
        print("UART connection test failed")
    
    print("Starting main control loop...")
    
    failed_requests = 0
    max_failed_requests = 5

    try:
        while True:
            # Get orientation data
            try:
                r = requests.get("http://192.168.31.244:5000/orientation", timeout=1)
                data = r.json()

                roll_rate = data['roll']
                pitch_rate = data['pitch']
                yaw_rate = data['yaw']

                # Map to motor speeds
                m1, m2, m3 = map_speed(roll_rate, pitch_rate, yaw_rate)

                # Check UART connection before sending
                if not check_uart_connection(uart):
                    print("UART connection lost, attempting to reconnect...")
                    close_uart(uart)
                    uart = setup_uart(UART_PORT, BAUD_RATE, TIMEOUT)
                    if uart is None:
                        print("Failed to reconnect UART, retrying in 5 seconds...")
                        time.sleep(5)
                        continue

                # Send to Pico
                if send_speeds(uart, m1, m2, m3, debug_mode):
                    # Receive from Pico (non-blocking)
                    actual_speeds = receive_speeds(uart, debug_mode)
                else:
                    print("Failed to send speeds to Pico")
                    actual_speeds = None

                # Save to buffer
                buffer.append({
                    "timestamp": time.time(),
                    "roll": data["roll"],
                    "pitch": data["pitch"],
                    "yaw": data["yaw"],
                    "m1_speed": m1,
                    "m2_speed": m2,
                    "m3_speed": m3,
                    "actual_speeds": actual_speeds
                })
                
                # Reset failed request counter on successful operation
                failed_requests = 0

                # Periodically dump to CSV
                if len(buffer) >= log_interval:
                    with open("orientation_log.csv", "a", newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=buffer[0].keys())
                        if f.tell() == 0:  # Write header if file is empty
                            writer.writeheader()
                        writer.writerows(buffer)
                    buffer.clear()

                time.sleep(0.016)  # ~60Hz polling

            except requests.exceptions.RequestException as e:
                print(f"HTTP request error: {e}")
                failed_requests += 1
                if failed_requests >= max_failed_requests:
                    print(f"Too many failed requests ({failed_requests}), stopping motors")
                    send_speeds(uart, 0, 0, 0, True)
                    failed_requests = 0
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                print(f"Processing error: {e}")
                # Stop motors on any processing error
                send_speeds(uart, 0, 0, 0, True)
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
        # Stop all motors before exiting
        try:
            send_speeds(uart, 0, 0, 0, True)
            print("Motors stopped")
        except:
            pass
    finally:
        if uart:
            close_uart(uart)

if __name__ == "__main__":
    main()