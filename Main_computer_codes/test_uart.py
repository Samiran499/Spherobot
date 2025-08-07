#!/usr/bin/env python3
"""
Test script for UART communication with RPi Pico
This script sends test speed commands and monitors responses
"""

import time
import math
from src.speed_uart import setup_uart, send_speeds, receive_speeds, close_uart

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
                time.sleep(0.5)
                response = receive_speeds(uart, True)
                if response:
                    print(f"  Response {i+1}: {response}")
            time.sleep(1)
        
        # Test 2: Send different speeds
        print("\nTest 2: Sending test speeds...")
        test_speeds = [
            (10, 0, 0),
            (0, 10, 0),
            (0, 0, 10),
            (5, 5, 5),
            (-5, -5, -5)
        ]
        
        for i, (m1, m2, m3) in enumerate(test_speeds):
            print(f"  Sending speeds: M1={m1}, M2={m2}, M3={m3}")
            if send_speeds(uart, m1, m2, m3, True):
                time.sleep(0.5)
                response = receive_speeds(uart, True)
                if response:
                    print(f"  Response: {response}")
            time.sleep(2)
        
        # Test 3: Continuous communication test
        print("\nTest 3: Continuous communication (10 seconds)...")
        start_time = time.time()
        counter = 0
        
        while time.time() - start_time < 10:
            # Send sinusoidal speeds for testing
            t = time.time() - start_time
            m1 = 10 * math.sin(t)
            m2 = 10 * math.sin(t + 2.094)  # 120 degrees phase shift
            m3 = 10 * math.sin(t + 4.188)  # 240 degrees phase shift
            
            if send_speeds(uart, m1, m2, m3, True):
                response = receive_speeds(uart, True)
                counter += 1
            
            time.sleep(0.1)  # 10Hz
        
        print(f"Completed {counter} successful transmissions in 10 seconds")
        
        # Test 4: Stop all motors
        print("\nTest 4: Stopping all motors...")
        for i in range(3):
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
