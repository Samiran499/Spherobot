#!/usr/bin/env python3
"""
Motor diagnostic tool for Spherobot
Helps correlate Python code with Pico motor behavior
"""

import time
import math
from src.speed_uart import setup_uart, send_speeds, close_uart

# UART Configuration
UART_PORT = "/dev/serial0"
BAUD_RATE = 115200
TIMEOUT = 1

def motor_diagnostics():
    """Run comprehensive motor diagnostics"""
    print("=== Spherobot Motor Diagnostics ===")
    print("This tool helps correlate the Python code with Pico motor behavior")
    print(f"Port: {UART_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    
    # Initialize UART
    uart = setup_uart(UART_PORT, BAUD_RATE, TIMEOUT)
    if uart is None:
        print("❌ Failed to initialize UART")
        return False
    
    print("✅ UART initialized successfully")
    print("⏳ Waiting for Pico to be ready...")
    time.sleep(3)
    
    try:
        # Test 1: Individual motor test
        print("\n" + "="*50)
        print("TEST 1: Individual Motor Testing")
        print("="*50)
        
        motors = ["Motor 1", "Motor 2", "Motor 3"]
        test_rpm = 25  # Safe starting RPM
        
        for i, motor_name in enumerate(motors):
            print(f"\n🔧 Testing {motor_name} at {test_rpm} RPM...")
            
            # Create speed array with only one motor active
            speeds = [0, 0, 0]
            speeds[i] = test_rpm
            
            if send_speeds(uart, speeds[0], speeds[1], speeds[2], True):
                print(f"✅ Command sent: M1={speeds[0]}, M2={speeds[1]}, M3={speeds[2]} RPM")
                print(f"👀 Observe {motor_name} - should rotate at {test_rpm} RPM")
                time.sleep(5)  # Give time to observe
                
                # Stop motor
                send_speeds(uart, 0, 0, 0, True)
                print(f"🛑 {motor_name} stopped")
                time.sleep(2)
            else:
                print(f"❌ Failed to send command for {motor_name}")
        
        # Test 2: RPM calibration
        print("\n" + "="*50)
        print("TEST 2: RPM Calibration")
        print("="*50)
        
        rpm_levels = [20, 30, 40, 50, 60]
        
        for rpm in rpm_levels:
            print(f"\n🔧 Testing all motors at {rpm} RPM...")
            if send_speeds(uart, rpm, rpm, rpm, True):
                print(f"✅ All motors should now run at {rpm} RPM")
                print("👀 Observe motor speeds - they should be synchronized")
                time.sleep(4)
            else:
                print(f"❌ Failed to send {rpm} RPM command")
        
        # Stop all motors
        send_speeds(uart, 0, 0, 0, True)
        print("🛑 All motors stopped")
        time.sleep(2)
        
        # Test 3: Direction test
        print("\n" + "="*50)
        print("TEST 3: Direction Testing")
        print("="*50)
        
        directions = [
            (30, 30, 30, "Forward"),
            (-30, -30, -30, "Reverse"),
            (30, -30, 0, "Mixed directions"),
            (0, 30, -30, "Alternating")
        ]
        
        for m1, m2, m3, description in directions:
            print(f"\n🔧 Testing: {description}")
            print(f"   M1={m1}, M2={m2}, M3={m3} RPM")
            if send_speeds(uart, m1, m2, m3, True):
                print(f"✅ Command sent successfully")
                print(f"👀 Observe motor directions: {description}")
                time.sleep(4)
            else:
                print(f"❌ Failed to send direction test command")
        
        # Stop all motors
        send_speeds(uart, 0, 0, 0, True)
        print("🛑 All motors stopped")
        time.sleep(2)
        
        # Test 4: Minimum RPM test
        print("\n" + "="*50)
        print("TEST 4: Minimum RPM Detection")
        print("="*50)
        
        min_rpm_test = [5, 10, 15, 20, 25]
        
        for rpm in min_rpm_test:
            print(f"\n🔧 Testing minimum RPM: {rpm}")
            if send_speeds(uart, rpm, rpm, rpm, True):
                print(f"✅ {rpm} RPM command sent")
                print(f"👀 Check if motors can maintain {rpm} RPM or if they stall")
                time.sleep(3)
            else:
                print(f"❌ Failed to send {rpm} RPM command")
        
        # Final stop
        send_speeds(uart, 0, 0, 0, True)
        print("\n🛑 All motors stopped - diagnostics complete")
        
        # Test 5: Correlation with Pico code
        print("\n" + "="*50)
        print("TEST 5: Pico Code Correlation Analysis")
        print("="*50)
        
        print("📋 Pico Code Analysis:")
        print("   • Target speed set in: motors[i].vt = speed (line ~101)")
        print("   • Velocity conversion: v = velocity / 1500.0*60.0 (line ~119)")
        print("   • PID control: kp=5.0, ki=10.0, kd=0.1 (line ~148)")
        print("   • PWM output: constrain((int)fabs(u), 0, 255) (line ~166)")
        print("   • Direction control: setMotor(dir, pwr, ...) (line ~167)")
        
        print("\n💡 What to observe:")
        print("   1. Motors should start moving at ~20 RPM minimum")
        print("   2. Speed should be proportional to RPM command")
        print("   3. Direction changes should be immediate")
        print("   4. Motors should stop cleanly when RPM = 0")
        
        print("\n🔧 If motors don't work:")
        print("   1. Check PID gains in Pico code (lines ~148-150)")
        print("   2. Verify encoder connections (pins 9-14)")
        print("   3. Check motor driver connections (pins 6-8, 16-21)")
        print("   4. Ensure UART1 is properly connected (Pi TX → Pico RX)")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Diagnostics interrupted by user")
        send_speeds(uart, 0, 0, 0, True)
        return False
    except Exception as e:
        print(f"❌ Diagnostics failed with error: {e}")
        return False
    finally:
        close_uart(uart)

if __name__ == "__main__":
    try:
        motor_diagnostics()
    except Exception as e:
        print(f"❌ Diagnostic script failed: {e}")
