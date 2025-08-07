# Spherobot Main Computer Codes

This directory contains the Python code that runs on the Raspberry Pi Zero 2W to control the Spherobot.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure UART on Raspberry Pi
The code uses the hardware UART (`/dev/serial0`) to communicate with the RPi Pico. Make sure UART is enabled:

1. Edit `/boot/config.txt` and add:
   ```
   enable_uart=1
   dtoverlay=disable-bt
   ```

2. Edit `/boot/cmdline.txt` and remove any references to `console=serial0,115200`

3. Reboot the Pi

### 3. Hardware Connections
Connect the RPi Zero 2W to the RPi Pico via UART:
- Pi Zero TX (GPIO 14) → Pico RX (UART1 RX)
- Pi Zero RX (GPIO 15) → Pico TX (UART1 TX)
- Ground connection between both devices

### 4. Test UART Communication
Before running the main program, test the UART communication:
```bash
python test_uart.py
```

### 5. Run the Main Program
```bash
python main.py
```

## File Description

- `main.py`: Main control loop that receives orientation data and controls the motors
- `src/kinematics_mapping.py`: Converts orientation data to motor speeds using kinematic equations
- `src/speed_uart.py`: UART communication functions for sending/receiving data to/from the Pico
- `test_uart.py`: Test script to verify UART communication
- `requirements.txt`: Python dependencies

## Configuration

### UART Settings
- Port: `/dev/serial0` (default Pi UART)
- Baud Rate: 115200
- Timeout: 1 second

### Control Loop
- Frequency: ~60Hz (16ms delay)
- Data logging: Every 100 samples to CSV

### Motor Speeds
Motor speeds are sent as comma-separated values in the format: `m1,m2,m3\n`
Example: `10.50,-5.25,0.00\n`

## Debugging

Set `debug_mode = True` in `main.py` to see detailed UART communication logs.
Set `debug_mode = False` for production use to reduce console output.

## Troubleshooting

1. **UART Permission Issues**: Add your user to the `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER
   ```

2. **Connection Lost**: The code automatically attempts to reconnect if UART connection is lost.

3. **No Response from Pico**: 
   - Check physical connections
   - Verify Pico is running the drive_unit code
   - Check if UART is enabled on Pi

4. **Import Errors**: Make sure all dependencies are installed:
   ```bash
   pip install pyserial requests numpy
   ```
