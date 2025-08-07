#!/usr/bin/env python3
"""
Configuration loader for Spherobot
Loads settings from config.ini file
"""

import configparser
import os

def load_config(config_file="config.ini"):
    """Load configuration from file"""
    config = configparser.ConfigParser()
    
    # Set default values
    defaults = {
        'orientation_server': {
            'ip': '192.168.31.244',
            'port': '5000',
            'endpoint_path': '/orientation',
            'timeout': '1'
        },
        'uart': {
            'port': '/dev/serial0',
            'baud_rate': '115200',
            'timeout': '1'
        },
        'control': {
            'frequency': '60',
            'max_failed_requests': '5'
        },
        'logging': {
            'log_interval': '100',
            'debug_mode': 'true',
            'csv_filename': 'orientation_log.csv'
        }
    }
    
    # Set defaults
    config.read_dict(defaults)
    
    # Try to read config file
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            print(f"Loaded configuration from {config_file}")
        except Exception as e:
            print(f"Error reading config file {config_file}: {e}")
            print("Using default configuration")
    else:
        print(f"Config file {config_file} not found, using defaults")
    
    return config

def get_orientation_endpoint(config):
    """Build orientation server endpoint URL"""
    ip = config.get('orientation_server', 'ip')
    port = config.getint('orientation_server', 'port')
    path = config.get('orientation_server', 'endpoint_path')
    return f"http://{ip}:{port}{path}"

def print_config(config):
    """Print current configuration"""
    print("\n=== Current Configuration ===")
    print(f"Orientation Server: {get_orientation_endpoint(config)}")
    print(f"Request Timeout: {config.getfloat('orientation_server', 'timeout')}s")
    print(f"UART Port: {config.get('uart', 'port')}")
    print(f"UART Baud Rate: {config.getint('uart', 'baud_rate')}")
    print(f"Control Frequency: {config.getint('control', 'frequency')} Hz")
    print(f"Debug Mode: {config.getboolean('logging', 'debug_mode')}")
    print("=" * 30)

if __name__ == "__main__":
    # Test the config loader
    config = load_config()
    print_config(config)
