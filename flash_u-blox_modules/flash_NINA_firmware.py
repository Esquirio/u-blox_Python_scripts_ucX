import serial
import json
import argparse
import os
import time
from tqdm import tqdm
from xmodem import XMODEM
from colorama import Fore, Back, Style, init
from ubxsa import UBXSerialAdapter
import re

# Initialize colorama
init(autoreset=True)

default_baudrate = 115200

# Global Variables
nina_family = ["NINA-B22X", "NINA-W13X", "NINA-W15X"]

def read_config(config_file: str) -> dict:
    config = {}
    try:
        with open(config_file, "r") as file:
            for line in file:
                # Skip comments or empty lines
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                # Parse key-value pairs
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip('"')
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Configuration file not found at {config_file}")
        return None
    return config

def load_JSON(config: dict) -> dict:
    # Get the directory of the current script
    script_dir = os.path.dirname(__file__)

    # Set the default JSON_FILE based on the MODULE value
    module = config.get("MODULE")
    if module in nina_family:

        json_file = f"{module}-CF-1.0.json"

        # Construct the relative path from the config
        relative_path = os.path.join("Firmwares", config.get("MODULE"),
            config.get("MODULE") + "-" + config.get("FW_VERSION"),
            json_file
        )
        
        if not relative_path:
            print(f"{Fore.RED}Error: PATH is required in the configuration file.")
            return
        
        # Construct the full path in a platform-independent way
        json_path = os.path.join(script_dir, *relative_path.split('/'))

        # Debug print to verify the path
        # print(f"{Fore.GREEN}Loading JSON file from path: {json_path}")

        # Load JSON file
        try:
            with open(json_path, "r") as file:
                data = json.load(file)[0]
        except FileNotFoundError:
            print(f"{Fore.RED}Error: JSON file not found at {json_path}")
            return

        # Extract parameters from JSON
        parameters = {
            "mode": 0,
            "module": config.get("MODULE"),  # Get the module name from the config file
            "fw": config.get("FW_VERSION"),  # Get the firmware version from the config file
            "port": config.get("COMPORT"),  # Get the COM port from the config file
            "baudrate": int(config.get("BAUDRATE")),  #Get the baudrate from the config file
            "flash_baudrate": int(config.get("FLASH_BAUDRATE")),  #Baudrate to flash the firmware
            "id": int(data["Id"], 16),  # Convert from hex to decimal
            "size": int(data["Size"], 16),    # Convert from hex to decimal
            "file": data["File"],  # Get "File" from JSON data
            "signature_file": data["SignatureFile"], # Get the signature file name from JSON data
            "name": data["Version"], # Get the complete firmware version name from JSON data
            "flags": data["Permissions"],  # Get the flags from the Permissions key
            "json_path": json_path,  # Get the flags from the Permissions key
            "signature": None  # None, it will be filled later
        }

        # Read the signature from the signature file (Local function)
        def read_signature(parameters):
            # Ensure the signature file exists in the same folder as the JSON
            signature_path = os.path.join(os.path.dirname(parameters["json_path"]), parameters["signature_file"])
            if not os.path.exists(signature_path):
                print(f"{Fore.RED}Error: Signature file not found at {signature_path}")
                return

            # Load the signature from TXT file
            with open(signature_path, "r") as file:
                parameters["signature"] = file.read().strip()

        read_signature(parameters)

        return parameters
    else:
        print(f"{Fore.RED}Error: Unsupported module {module}")
        return None

def flash_nina_fw(parameters: dict, ubx_port: UBXSerialAdapter, ser: serial.Serial, previous_fw_version):
    if not parameters["port"]:
        print(f"{Fore.RED}Error: COMPORT is required in the configuration file.")
        return

    # Construct AT command with flags
    at_command = (f"AT+UFWUPD={parameters['mode']},{parameters['flash_baudrate']},"
                  f"{parameters['id']},{parameters['size']},"
                  f"{parameters['signature']},{parameters['name']},{parameters['flags']}")

    # Send the AT command
    print(f"{Fore.GREEN}*** Sending the AT Command to flash {parameters['module']}X-{parameters['fw']} ***")
    print(f"{Fore.YELLOW}{Style.DIM}{at_command}\n")
    ubx_port.send_command(at_command)

    # Now, wait for the sequence of 3 'C' characters
    print(f"{Fore.GREEN}*** Ready to send fw via XMODEM... ***")
    c_count = 0
    while c_count < 3:
        byte = ubx_port.read()
        # Flush the input buffer
        ser.reset_input_buffer()

        if byte == b'C':
            c_count += 1
            print(f"{Back.WHITE}{Fore.BLACK}{byte.decode('utf-8')}", end="")
        elif byte:
            c_count = 0  # Reset if something else is received

    # Record the start time
    start_time = time.time()
    
    print(f"{Fore.GREEN}\n\n*** Starting XMODEM file transfer... ***")

    # Prepare XMODEM file transfer
    file_path = os.path.join(os.path.dirname(parameters["json_path"]), parameters["file"])
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Error: File {file_path} not found for transfer.")
        return None

    # Get the size of the file to transfer
    file_size = os.path.getsize(file_path)

    # Initialize the progress bar
    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Transferring File", ncols=100)

    def progress_callback(total_packets, success_count, error_count):
        """ Progress callback to update the progress bar """
        packet_size = 128 # or 1024 for XMODEM-1K
        bytes_transferred = success_count * packet_size
        progress_bar.update(bytes_transferred - progress_bar.n)

    # Start the XMODEM transfer
    with open(file_path, "rb") as f:
        def getc(size, timeout=1):
            """ XMODEM getc callback function to receive data from UART """
            byte = ubx_port.read(1)  # Read 1 byte from the UART connection
            if byte:
                return byte
            return None

        def putc(data, timeout=1):
            """ XMODEM putc callback function to send data to UART """
            ubx_port.write(data)  # Write data to the UART connection
            return len(data)

        modem = XMODEM(getc, putc)  # Using both getc and putc functions
        # Set the progress callback
        modem.send(f, callback=progress_callback)
        
        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time

        progress_bar.close()
        print(f"{Fore.GREEN}*** File transfer completed. ***")


    # Print elapsed time and transfer details
    print(f"{Fore.CYAN}\nTotal time taken for transfer: {elapsed_time:.2f} seconds")
    print(f"{Fore.CYAN}Transfer speed: {file_size / elapsed_time / 1024:.2f} KB/s\n")

    # Function to extract the version information
    def extract_version_info(s):
        match = re.match(r'"(\d+\.\d+\.\d+)-', s)
        if match:
            return match.group(1)
        return None
    
    # Set baudrate back to default if firmware version is different
    if extract_version_info(previous_fw_version) != parameters["fw"]:
        ser.baudrate = default_baudrate
        print(f"{Fore.GREEN}*** Baudrate set back to default: 115200 bps ***")
        # Update the ubx_port baudrate
        ubx_port._stream.baudrate = default_baudrate

    return ubx_port

def main(config_file: str):
    # Read configuration
    config = read_config(config_file)
    if not config:
        return

    # Load JSON file and extract parameters
    parameters = load_JSON(config)


    if parameters["module"] in nina_family:
        if parameters["module"] in nina_family:
            # Open the serial port
            try:
                with serial.Serial(parameters["port"], parameters["baudrate"], timeout=2) as ser:
                    print(f"{Fore.GREEN}*** Openning UART - COMPORT: {parameters['port']}, baudrate: {parameters['baudrate']} ***\n")
                    
                    # Reset input and output buffers
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()

                    ser.readline()
                    ser.readline()
                    
                    # Create a UBXSerialAdapter object
                    ubx_port = UBXSerialAdapter(ser)

                    # Check the firmware version before flashing
                    ubx_port.send_command("ATI9")
                    full_resp = ubx_port.wait_for_response("OK")

                    previous_fw_version = full_resp[full_resp.find('"'):full_resp.rfind('"') + 1]
                    print(f"{Fore.GREEN}*** Before flashing: ***\nFW Version: {previous_fw_version}")

                    # Set baudrate back to default if firmware version is different
                    if parameters['baudrate'] != parameters['flash_baudrate']:
                        ubx_port.send_command(f"AT+UMRS={parameters['flash_baudrate']},1,8,1,1,0")
                        ubx_port.wait_for_response("OK")
                        print("AT+UMRS OK received")
                        ubx_port.reboot_device()
                        time.sleep(1)

                        ser.close()
                        ser.__del__()
                        time.sleep(1)

                        ser = serial.Serial(parameters["port"], parameters["flash_baudrate"], timeout=2)
                        # Reset input and output buffers
                        ser.reset_input_buffer()
                        ser.reset_output_buffer()

                        ser.readline()
                        ser.readline()

                        # ser.baudrate = parameters['flash_baudrate']
                        print(f"{Fore.GREEN}*** Baudrate set to: {parameters['flash_baudrate']} bps ***")
                        # Update the ubx_port baudrate
                        ubx_port = UBXSerialAdapter(ser)
                        # ubx_port._stream.baudrate = parameters['flash_baudrate']
                        print("Baudrate updated")
                        ubx_port.send_command("AT")
                        ubx_port.wait_for_response("OK")
                        print("OK received")
                        
                    # Flash the firmware
                    ubx_port = flash_nina_fw(parameters, ubx_port, ser, previous_fw_version)
                    
                    # Wait for the +STARTUP message
                    resp = ubx_port.wait_for_startup()              
                    print(f"{Fore.YELLOW}{Style.DIM}{resp} received")
                    
                    # Check the firmware version after flashing
                    ubx_port.send_command("ATI9")
                    full_resp = ubx_port.wait_for_response("OK")
                    new_fw_version = full_resp[full_resp.find('"'):full_resp.rfind('"') + 1]
                    print(f"{Fore.GREEN}*** After flashing: ***\nFW Version: {new_fw_version}")

                    # Close the serial port
                    ser.close()
                    ser. __del__()

            except serial.SerialException as e:
                print(f"{Fore.RED}Error: {e}")
    else:
        print(f"{Fore.RED}Error: Unsupported module {parameters['module']}")
        return None

if __name__ == "__main__":
    # Parse command-line argument for the config file
    parser = argparse.ArgumentParser(description="Send an AT command through serial communication.")
    parser.add_argument(
        "--file", "-f", 
        required=True, 
        help="The path to the configuration file."
    )
    args = parser.parse_args()

    # Run the main function with the config file
    main(args.file)
