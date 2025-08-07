#!/usr/bin/env python3
"""
Quick IP address changer for Spherobot
Usage: python change_ip.py [new_ip_address]
"""

import sys
import configparser
import os

def change_ip(new_ip):
    """Change the orientation server IP address in config.ini"""
    config_file = "config.ini"
    
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found!")
        print("Run this script from the Main_computer_codes directory")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Get current IP
        current_ip = config.get('orientation_server', 'ip')
        print(f"Current IP: {current_ip}")
        
        # Update IP
        config.set('orientation_server', 'ip', new_ip)
        
        # Write back to file
        with open(config_file, 'w') as f:
            config.write(f)
        
        print(f"IP address changed to: {new_ip}")
        print(f"New endpoint: http://{new_ip}:{config.get('orientation_server', 'port')}/orientation")
        return True
        
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python change_ip.py [new_ip_address]")
        print("Example: python change_ip.py 192.168.1.100")
        
        # Show current IP
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
            current_ip = config.get('orientation_server', 'ip')
            print(f"\nCurrent IP: {current_ip}")
        except:
            print("Could not read current config")
        
        return
    
    new_ip = sys.argv[1]
    
    # Basic IP validation
    parts = new_ip.split('.')
    if len(parts) != 4:
        print("Error: Invalid IP address format")
        return
    
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                print("Error: Invalid IP address range")
                return
    except ValueError:
        print("Error: Invalid IP address format")
        return
    
    # Change the IP
    if change_ip(new_ip):
        print("\nIP address updated successfully!")
        print("Restart the main program to use the new IP address.")
    else:
        print("Failed to update IP address")

if __name__ == "__main__":
    main()
