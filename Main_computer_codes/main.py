import csv
import requests
import serial
import time
from src.kinematics_mapping import map_speed
from src.speed_uart import setup_uart, send_speeds, check_uart_connection, close_uart
from src.config_loader import load_config, get_orientation_endpoint, print_config

# Load configuration
config = load_config()

# Extract configuration values
ORIENTATION_ENDPOINT = get_orientation_endpoint(config)
UART_PORT = config.get('uart', 'port')
BAUD_RATE = config.getint('uart', 'baud_rate')
TIMEOUT = config.getfloat('uart', 'timeout')
CONTROL_FREQUENCY = config.getint('control', 'frequency')
REQUEST_TIMEOUT = config.getfloat('orientation_server', 'timeout')
MAX_FAILED_REQUESTS = config.getint('control', 'max_failed_requests')
RPM_SCALE_FACTOR = config.getfloat('control', 'rpm_scale_factor')
MAX_RPM = config.getfloat('control', 'max_rpm')
LOG_INTERVAL = config.getint('logging', 'log_interval')
DEBUG_MODE = config.getboolean('logging', 'debug_mode')
CSV_FILENAME = config.get('logging', 'csv_filename')

buffer = []
log_interval = LOG_INTERVAL
debug_mode = DEBUG_MODE

def main():
    print("Starting Spherobot Main Computer...")
    print_config(config)
    
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
    max_failed_requests = MAX_FAILED_REQUESTS

    try:
        while True:
            # Get orientation data
            try:
                r = requests.get(ORIENTATION_ENDPOINT, timeout=REQUEST_TIMEOUT)
                data = r.json()

                roll_rate = data['roll']
                pitch_rate = data['pitch']
                yaw_rate = data['yaw']

                # Map to motor speeds
                m1, m2, m3 = map_speed(roll_rate, pitch_rate, yaw_rate)
                
                # Scale to RPM (adjust this multiplier based on your system)
                # The kinematics output is in rad/s, convert to RPM with appropriate scaling
                m1_rpm = m1 * RPM_SCALE_FACTOR
                m2_rpm = m2 * RPM_SCALE_FACTOR  
                m3_rpm = m3 * RPM_SCALE_FACTOR
                
                # Limit maximum RPM to prevent motor damage
                m1_rpm = max(-MAX_RPM, min(MAX_RPM, m1_rpm))
                m2_rpm = max(-MAX_RPM, min(MAX_RPM, m2_rpm))
                m3_rpm = max(-MAX_RPM, min(MAX_RPM, m3_rpm))

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
                if send_speeds(uart, m1_rpm, m2_rpm, m3_rpm, debug_mode):
                    if debug_mode:
                        print(f"Successfully sent speeds: M1={m1_rpm:.2f}, M2={m2_rpm:.2f}, M3={m3_rpm:.2f} RPM")
                else:
                    print("Failed to send speeds to Pico")

                # Save to buffer
                buffer.append({
                    "timestamp": time.time(),
                    "roll": data["roll"],
                    "pitch": data["pitch"],
                    "yaw": data["yaw"],
                    "m1_speed": m1_rpm,
                    "m2_speed": m2_rpm,
                    "m3_speed": m3_rpm
                })
                
                # Reset failed request counter on successful operation
                failed_requests = 0

                # Periodically dump to CSV
                if len(buffer) >= log_interval:
                    with open(CSV_FILENAME, "a", newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=buffer[0].keys())
                        if f.tell() == 0:  # Write header if file is empty
                            writer.writeheader()
                        writer.writerows(buffer)
                    buffer.clear()

                time.sleep(1.0 / CONTROL_FREQUENCY)  # Control loop frequency

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