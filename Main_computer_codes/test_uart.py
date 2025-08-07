#!/usr/bin/env python3
"""
Test script for UART communication with RPi Pico
This script sends test speed commands and monitors responses
"""

import time
import math
from src.speed_uart import setup_uart, send_speeds, close_uart

# UART Configuration
UART_PORT = "/dev/serial0"
BAUD_RATE = 115200
TIMEOUT = 1

def test_uart_communication():
    """Test UART communication with the Pico"""
    print("=== UART Communication Test ===")
    print(f"Port: {UART_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    
    # Initialize UART
    uart = setup_uart(UART_PORT, BAUD_RATE, TIMEOUT)
    if uart is None:
        print("Failed to initialize UART")
        return False
    
    print("UART initialized successfully")
    print("Waiting for Pico to be ready...")
    time.sleep(3)
    
    try:
        # Test 1: Send zero speeds
        print("\nTest 1: Sending zero speeds...")
        for i in range(3):
            if send_speeds(uart, 0, 0, 0, True):
                print(f"  Successfully sent zero speeds (attempt {i+1})")
                time.sleep(0.5)
            else:
                print(f"  Failed to send zero speeds (attempt {i+1})")
            time.sleep(1)
        
        # Test 2: Send different speeds (in RPM - minimum 20 RPM to avoid stalling)
        print("\nTest 2: Sending test speeds (RPM values)...")
        test_speeds = [
            (30, 0, 0),    # Motor 1: 30 RPM
            (0, 30, 0),    # Motor 2: 30 RPM  
            (0, 0, 30),    # Motor 3: 30 RPM
            (25, 25, 25),  # All motors: 25 RPM
            (-25, -25, -25), # All motors: -25 RPM (reverse)
            (50, -30, 20)  # Mixed speeds
        ]
        
        for i, (m1, m2, m3) in enumerate(test_speeds):
            print(f"  Sending speeds: M1={m1} RPM, M2={m2} RPM, M3={m3} RPM")
            if send_speeds(uart, m1, m2, m3, True):
                print(f"  Successfully sent test speeds")
                time.sleep(1.0)  # Give motors time to reach target speed
            else:
                print(f"  Failed to send test speeds")
            time.sleep(3)  # Wait longer to observe motor behavior
        
        # Test 2.5: Step RPM test to find minimum working speed
        print("\nTest 2.5: Step RPM test (finding minimum speed)...")
        step_speeds = [5, 10, 15, 20, 25, 30, 40, 50]
        
        for rpm in step_speeds:
            print(f"  Testing {rpm} RPM on all motors...")
            if send_speeds(uart, rpm, rpm, rpm, True):
                print(f"  Command sent successfully - observe motors for {rpm} RPM")
                time.sleep(4)  # Give time to observe each speed level
            else:
                print(f"  Failed to send {rpm} RPM command")
        
        # Stop after step test
        print("  Stopping motors after step test...")
        send_speeds(uart, 0, 0, 0, True)
        time.sleep(2)
        
        # Test 3: Continuous communication test with varying RPM
        print("\nTest 3: Continuous communication with sinusoidal RPM (20 seconds)...")
        start_time = time.time()
        counter = 0
        
        while time.time() - start_time < 20:  # Extended to 20 seconds
            # Send sinusoidal speeds for testing (amplitude 30 RPM, offset 0)
            t = time.time() - start_time
            m1 = 30 * math.sin(t * 0.5)  # Slower frequency, 30 RPM amplitude
            m2 = 30 * math.sin(t * 0.5 + 2.094)  # 120 degrees phase shift
            m3 = 30 * math.sin(t * 0.5 + 4.188)  # 240 degrees phase shift
            
            if send_speeds(uart, m1, m2, m3, False):  # Silent mode for continuous test
                counter += 1
            
            # Print occasional status
            if counter % 20 == 0:
                print(f"  Status: {counter} commands sent, current speeds: M1={m1:.1f}, M2={m2:.1f}, M3={m3:.1f} RPM")
            
            time.sleep(0.2)  # 5Hz for better observation
        
        print(f"Completed {counter} successful transmissions in 20 seconds")
        
        # Test 4: Stop all motors
        print("\nTest 4: Stopping all motors...")
        for i in range(5):  # Send stop command multiple times
            send_speeds(uart, 0, 0, 0, True)
            time.sleep(0.5)
        
        print("\nUART communication test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        send_speeds(uart, 0, 0, 0, True)  # Stop motors
        return False
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    finally:
        close_uart(uart)

if __name__ == "__main__":
    try:
        test_uart_communication()
    except Exception as e:
        print(f"Test script failed: {e}")
