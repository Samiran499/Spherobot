#!/usr/bin/env python3
"""
Hardware check script for Spherobot
Verifies UART configuration and basic system setup
"""

import os
import subprocess
import sys

def check_uart_devices():
    """Check if UART devices are available"""
    print("=== UART Device Check ===")
    
    uart_devices = ["/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0"]
    
    for device in uart_devices:
        if os.path.exists(device):
            try:
                # Get device info
                result = subprocess.run(['ls', '-la', device], 
                                      capture_output=True, text=True)
                print(f"✓ {device} exists: {result.stdout.strip()}")
            except Exception as e:
                print(f"✗ Error checking {device}: {e}")
        else:
            print(f"✗ {device} not found")

def check_uart_config():
    """Check UART configuration in boot files"""
    print("\n=== UART Configuration Check ===")
    
    # Check config.txt
    config_file = "/boot/config.txt"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                if "enable_uart=1" in content:
                    print("✓ enable_uart=1 found in config.txt")
                else:
                    print("✗ enable_uart=1 NOT found in config.txt")
                    print("  Add 'enable_uart=1' to /boot/config.txt")
                
                if "dtoverlay=disable-bt" in content:
                    print("✓ dtoverlay=disable-bt found in config.txt")
                else:
                    print("⚠ dtoverlay=disable-bt NOT found in config.txt")
                    print("  Consider adding 'dtoverlay=disable-bt' to /boot/config.txt")
        except Exception as e:
            print(f"✗ Error reading config.txt: {e}")
    else:
        print("✗ /boot/config.txt not found")
    
    # Check cmdline.txt
    cmdline_file = "/boot/cmdline.txt"
    if os.path.exists(cmdline_file):
        try:
            with open(cmdline_file, 'r') as f:
                content = f.read()
                if "console=serial0" in content:
                    print("⚠ console=serial0 found in cmdline.txt")
                    print("  Remove console=serial0,115200 from /boot/cmdline.txt")
                else:
                    print("✓ console=serial0 NOT found in cmdline.txt")
        except Exception as e:
            print(f"✗ Error reading cmdline.txt: {e}")
    else:
        print("✗ /boot/cmdline.txt not found")

def check_python_deps():
    """Check if required Python packages are installed"""
    print("\n=== Python Dependencies Check ===")
    
    required_packages = ['serial', 'requests', 'numpy']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            if package == 'serial':
                print("  Install with: pip install pyserial")
            else:
                print(f"  Install with: pip install {package}")

def check_permissions():
    """Check user permissions for UART access"""
    print("\n=== Permission Check ===")
    
    try:
        # Check if user is in dialout group
        result = subprocess.run(['groups'], capture_output=True, text=True)
        if 'dialout' in result.stdout:
            print("✓ User is in dialout group")
        else:
            print("✗ User is NOT in dialout group")
            print("  Add with: sudo usermod -a -G dialout $USER")
            print("  Then log out and back in")
    except Exception as e:
        print(f"✗ Error checking groups: {e}")

def check_gpio_usage():
    """Check if GPIO pins are in use"""
    print("\n=== GPIO Usage Check ===")
    
    try:
        # Check if any process is using the UART
        result = subprocess.run(['lsof', '/dev/serial0'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("⚠ /dev/serial0 is currently in use:")
            print(result.stdout)
        else:
            print("✓ /dev/serial0 is not in use")
    except FileNotFoundError:
        print("⚠ lsof command not found, cannot check usage")
    except Exception as e:
        print(f"✗ Error checking GPIO usage: {e}")

def main():
    print("Spherobot Hardware Check")
    print("=" * 50)
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' not in f.read():
                print("⚠ This doesn't appear to be a Raspberry Pi")
    except:
        pass
    
    check_uart_devices()
    check_uart_config()
    check_python_deps()
    check_permissions()
    check_gpio_usage()
    
    print("\n=== Summary ===")
    print("If you see any ✗ marks above, please fix those issues before running the main program.")
    print("⚠ warnings are optional but recommended for best performance.")

if __name__ == "__main__":
    main()
