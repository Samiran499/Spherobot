# Spherobot Main Compu### 3. Configure UART on Raspb### 5. Test Hardware Setup
Check the hardware configuration:
```bash
python check_hardware.py
```

### 6. Test UART Communication
Before running the main program, test the UART communication:
```bash
python test_uart.py
```

### 7. Run Motor Diagnostics (Recommended)
To correlate with the Pico code and ensure proper motor operation:
```bash
python motor_diagnostics.py
```
This will test individual motors, RPM levels, directions, and help identify the minimum working RPM.

### 8. Run the Main Program
```bash
python main.py
```

## Configuration

All settings can be modified in `config.ini`:

- **Orientation Server**: Change IP address, port, and timeout
- **UART Settings**: Port, baud rate, timeout
- **Control Loop**: Frequency and error handling
- **Logging**: CSV filename, debug mode, log interval

## File Description

- `main.py`: Main control loop that receives orientation data and controls the motors
- `config.ini`: Configuration file for all settings
- `src/config_loader.py`: Configuration file loader utility
- `src/kinematics_mapping.py`: Converts orientation data to motor speeds using kinematic equations
- `src/speed_uart.py`: UART communication functions for sending data to the Pico
- `motor_diagnostics.py`: Comprehensive motor testing script that correlates with Pico code
- `test_uart.py`: Test script to verify UART communication
- `check_hardware.py`: Hardware setup verification script
- `requirements.txt`: Python dependenciesuses the hardware UART (`/dev/serial0`) to communicate with the RPi Pico. Make sure UART is enabled:

1. Edit `/boot/config.txt` and add:
   ```
   enable_uart=1
   dtoverlay=disable-bt
   ```

2. Edit `/boot/cmdline.txt` and remove any references to `console=serial0,115200`

3. Reboot the Pi

### 4. Hardware Connectionshis directory contains the Python code that runs on the Raspberry Pi Zero 2W to control the Spherobot.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Settings
Edit `config.ini` to change the orientation server IP address and other settings:

```ini
[orientation_server]
ip = 192.168.1.100  # Change this to your server IP
port = 5000
```

You can also modify other settings like UART port, control frequency, etc. in this file.

### 3. Configure UART on Raspberry Pi
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

## Quick IP Address Change

To quickly change the orientation server IP address, edit the `config.ini` file:

```ini
[orientation_server]
ip = YOUR_NEW_IP_ADDRESS
```

No code modification required!

## Motor Communication

Motor speeds are sent as comma-separated RPM values in the format: `m1,m2,m3\n`
Example: `25.50,-30.25,0.00\n`

**Important**: 
- The Pico expects RPM values, not raw speed values
- Minimum RPM: ~20 to avoid motor stalling
- Maximum RPM: 100 (configurable in config.ini)
- The system automatically scales orientation data to appropriate RPM values

**Pico Code Correlation**:
- Target speeds set in `motors[i].vt` (Pico line ~101)
- PID control with kp=5.0, ki=10.0, kd=0.1 (Pico lines ~148-150)
- Encoder feedback via interrupts (Pico lines ~78-87)

**Note**: The system currently only sends speeds to the Pico and does not receive feedback. This simplifies communication and reduces latency.

## Control Loop Settings

- Default Frequency: 60Hz (configurable in `config.ini`)
- Request Timeout: 1 second (configurable)
- Auto-stop: Motors stop after 5 consecutive failed requests (configurable)

## Debugging

Set `debug_mode = true` in `config.ini` to see detailed UART communication logs.
Set `debug_mode = false` for production use to reduce console output.

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
