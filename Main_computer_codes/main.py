import csv
import requests
import serial
import time
from src.kinematics_mapping import map_speed
from src.speed_uart import setup_uart, send_speeds, receive_speeds

# UART Configuration
UART_PORT = "/dev/serial0"  # Default UART port on Pi Zero
BAUD_RATE = 115200
TIMEOUT = 1

buffer = []
log_interval = 100  # How many samples before writing to CSV

def main():
    uart = setup_uart()
    if uart is None:
        return

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

                # Send to Pico
                send_speeds(uart, m1, m2, m3)

                # Receive from Pico (non-blocking)
                receive_speeds(uart)

                # Save to buffer
                buffer.append({
                    "timestamp": time.time(),
                    "roll": data["roll"],
                    "pitch": data["pitch"],
                    "yaw": data["yaw"],
                    "m1_speed": m1,
                    "m2_speed": m2,
                    "m3_speed": m3
                })

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
                time.sleep(1)  # Wait before retrying
            except Exception as e:
                print(f"Processing error: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if uart:
            uart.close()

if __name__ == "__main__":
    main()