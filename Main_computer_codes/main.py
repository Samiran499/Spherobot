import csv
import requests
#import serial
import time
from src.kinematics_mapping import map_speed

buffer = []
log_interval = 100  # How many samples before writing to CSV

while True:
    try:
        r = requests.get("http://192.168.31.244:5000/orientation", timeout=1)
        data = r.json()

        roll_rate = data['roll']
        pitch_rate = data['pitch']
        yaw_rate = data['yaw']

        m1, m2, m3 = map_speed(roll_rate, pitch_rate, yaw_rate)

        # Send to Pico
        command = f"{m1},{m2},{m3}\n"
        print(command)

        # Save to buffer
        buffer.append({
            "timestamp": time.time(),
            "roll": data["roll"],
            "pitch": data["pitch"],
            "yaw": data["yaw"]
        })

        # Periodically dump to CSV
        if len(buffer) >= log_interval:
            with open("orientation_log.csv", "a", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=buffer[0].keys())
                writer.writerows(buffer)
            buffer.clear()  # Clear after saving

        time.sleep(0.016)  # ~60Hz polling

    except Exception as e:
        print("Error:", e)