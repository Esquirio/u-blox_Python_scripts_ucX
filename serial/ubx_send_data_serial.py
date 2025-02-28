#!/usr/bin/env python
import time
from datetime import datetime
import serial
import argparse
import random
import string
import json
from colorama import init, Fore, Style, Back

import SPA

init(autoreset=True)

debug = False

def myTimeStamp():    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return timestamp

def format_mac_address(mac):
    """
    Formats the MAC address to remove colons if they are included.

    :param mac: The MAC address as a string.
    :return: The formatted MAC address.
    """
    return mac.replace(':', '')

def generate_random_data(length):
    """
    Generates a random string of the specified length, starting with "u-blox" and ending with "AE-SHO".

    :param length: The length of the random string.
    :return: A random string of the specified length.
    """
    if length < 12:
        random_length = length
        data_generated = ''.join(random.choices(string.ascii_letters + string.digits, k=random_length))
    else:
        prefix = "u_blox"
        suffix = "AE_SHO"
        random_length = length - len(prefix) - len(suffix)
        data_generated = prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=random_length)) + suffix
    
    time.sleep(.1)
    
    if debug:
        print(f"{Fore.GREEN}Data generated: {data_generated}")

    return data_generated

def send_data(port, data, i):
    """
    Sends the specified data via the specified serial port.

    :param port: The serial port to use.
    :param data: The data to send.
    """
    try:
        if debug:
            print(f"{Fore.CYAN}{i}. Sending data ...")
        # Send data
        port.write(data.encode())
    except serial.SerialException as e:
        print(f"{Fore.RED}Serial error: {e}")

def configure_module(spa, target_address):
    global debug
    if debug:
        print(f"{Fore.CYAN}Configuring module")

    # Reset device
    spa.enterCommandMode() # +++ 1s +++
    spa.command("AT+UFACTORY")
    spa.command("AT+CPWROFF")
    spa.waitForStartup()
    if debug:
        print(f"{Fore.CYAN}Factory reset complete")

    # Set Central
    spa.command("AT+UBTMODE=1")
    spa.command("AT&W")
    spa.command("AT+CPWROFF")
    spa.waitForStartup()
    if debug:
        print(f"{Fore.CYAN}Bluetooth BR/EDR mode set")
    
    if debug:
        print(f"{Fore.CYAN}Configuring SPP")
    spa.command(f"AT+UDCP=spp://{target_address}")
    spa.waitForResponse("+UUDPC:")

    if debug:
        print(f"{Fore.YELLOW}+UUDPC received")
    spa.enterDataMode()
    if debug:
        print(f"{Fore.CYAN}Required delay for data mode or extended data mode")
    time.sleep(0.1)

def open_serial(com_port, baudrate, rtscts=True):
    global debug
    if debug:
        print(f"{Fore.CYAN}Opening serial port {Fore.YELLOW}{com_port} {Fore.CYAN}at {Fore.YELLOW}{baudrate} {Fore.CYAN}baud")

    port = serial.Serial(com_port, baudrate, rtscts=rtscts, timeout=1)
    port.reset_input_buffer()
    port.reset_output_buffer()
    return port

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def main():
    global debug
    parser = argparse.ArgumentParser(description="Send data to a u-blox module via serial.")
    parser.add_argument('-c','--config', help='The path to the configuration file.', default='modules.json')
    args = parser.parse_args()

    config = load_config(args.config)

    transmitter_config = config['transmitter']
    receiver_config = config['receiver']
    data_config = config['data']
    debug_config = config['debug']

    debug = debug_config['debug']
    
    target_address = format_mac_address(receiver_config['mac_address'])
    if debug:
        print(f"{Fore.GREEN}Target address: {Fore.YELLOW}{target_address}")

    transmitter = open_serial(transmitter_config['COMPORT'], transmitter_config['baudrate'], rtscts=True)
    transmitter.reset_input_buffer()
    transmitter.reset_output_buffer()
    spa_transmitter = SPA.SPA(transmitter)

    configure_module(spa_transmitter, target_address)
    
    start = myTimeStamp()
    data = generate_random_data(data_config['data_size'])

    for i in range(data_config['xtimes']):
        send_data(transmitter, data, i + 1)
        time.sleep(data_config['interval_ms'] / 1000.0)  # Convert milliseconds to seconds
    stop = myTimeStamp()

if __name__=='__main__':
    main()
