import serial
import json
import argparse
import os
import time
from tqdm import tqdm
from xmodem import XMODEM
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Global Variables
u_blox_module_names = ["NINA-B22X", "NINA-W13X", "NINA-W15X", "NORA-W36X"]
nina_family = [name for name in u_blox_module_names if name.startswith("NINA")]
nora_family = [name for name in u_blox_module_names if name.startswith("NORA")]
flash_baud_rate = 921600

def read_config(config_file):
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

def load_JSON(config):
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
    elif module in nora_family:
        print(f"{Fore.RED}TODO: {module}")  
        return None
    else:
        print(f"{Fore.RED}Error: Unsupported module {module}")
        return None

def flash_nina_fw(parameters, ser):
    if not parameters["port"]:
        print(f"{Fore.RED}Error: COMPORT is required in the configuration file.")
        return
    
    # Construct AT command with flags
    at_command = (f'AT+UFWUPD={parameters["mode"]},{parameters["baudrate"]},'
                  f'{parameters["id"]},{parameters["size"]},'
                  f'{parameters["signature"]},{parameters["name"]},{parameters["flags"]}')

    # Send the AT command
    print(f"{Fore.GREEN}*** Sending the AT Command to flash {parameters["module"]}X-{parameters["fw"]} ***")
    print(f"{Fore.YELLOW}{Style.DIM}{at_command}\n")
    ser.write(at_command.encode() + b"\r\n")

    # Record the start time
    start_time = time.time()

    # Now, wait for the sequence of 3 'C' characters
    print(f"{Fore.GREEN}*** Ready to send fw via XMODEM... ***")
    c_count = 0
    while c_count < 3:
        byte = ser.read()
        # Flush the input buffer
        ser.reset_input_buffer()

        if byte == b'C':
            c_count += 1
            print(f"{Back.WHITE}{Fore.BLACK}{byte.decode('utf-8')}", end="")
        elif byte:
            c_count = 0  # Reset if something else is received

    print(f"{Fore.GREEN}\n\n*** Starting XMODEM file transfer... ***")

    # Prepare XMODEM file transfer
    file_path = os.path.join(os.path.dirname(parameters["json_path"]), parameters["file"])
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Error: File {file_path} not found for transfer.")
        return

    # Get the size of the file to transfer
    file_size = os.path.getsize(file_path)

    # Initialize the progress bar
    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Transferring File", ncols=80)

    def progress_callback(total_packets, success_count, error_count):
        """ Progress callback to update the progress bar """
        packet_size = 128  # or 1024 for XMODEM-1K
        bytes_transferred = success_count * packet_size
        progress_bar.update(bytes_transferred - progress_bar.n)

    # Start the XMODEM transfer
    with open(file_path, "rb") as f:
        def getc(size, timeout=1):
            """ XMODEM getc callback function to receive data from UART """
            byte = ser.read(1)  # Read 1 byte from the UART connection
            if byte:
                return byte
            return None

        def putc(data, timeout=1):
            """ XMODEM putc callback function to send data to UART """
            ser.write(data)  # Write data to the UART connection
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

# def update_flash_baudrate(parameters, ser):
#     # Updating the serial baudrate
#     print(f"{Fore.CYAN}### Changing the baud rate to {parameters["baudrate"]}... ###")
    
#     at_command = f"AT+UMRS={parameters["baudrate"]},1,8,1,1,0"

#     # Send the AT command
#     print(f"{Fore.GREEN}*** Sending the AT Command to flash {u_blox_module}X-{fw_version} ***")
#     print(f"{Fore.YELLOW}{Style.DIM}{at_command}\n")
#     ser.write(at_command.encode() + b"\r\n")
#     [full_resp, r] = spa.command(f"AT+UMRS={flash_baud_rate},1,8,1,1,0")
#     print(f"{Fore.YELLOW}{Style.DIM}full_resp = {full_resp}  r = {r}")
#     ser.write(f"AT&W\r\n".encode())
#     [full_resp, r] = spa.command("AT&W")
#     print(f"{Fore.YELLOW}{Style.DIM}full_resp = {full_resp}  r = {r}")
#     [full_resp, r] = spa.command("AT+CPWROFF")
#     print(f"{Fore.YELLOW}{Style.DIM}full_resp = {full_resp}  r = {r}")
#     time.sleep(1)
#     parameters["baudrate"] = flash_baud_rate
#     ser.baudrate = parameters["baudrate"]
#     print(f"{Fore.GREEN}*** Baud rate changed to {parameters["baudrate"]} ***")
#     r = spa.waitForStartup()
#     print(f"{Fore.YELLOW}{Style.DIM}r = {r}")
#     ser.reset_input_buffer()
#     ser.reset_output_buffer()
#     [full_resp, r] = spa.command("ATI9")
#     print(f"{Fore.YELLOW}{Style.DIM}full_resp = {full_resp}  r = {r}")

def main(config_file):
    # Read configuration
    config = read_config(config_file)
    if not config:
        return

    # Load JSON file and extract parameters
    parameters = load_JSON(config)


    if parameters["module"] in u_blox_module_names:
        if parameters["module"] in nina_family:
            # Open the serial port
            try:
                with serial.Serial(parameters["port"], parameters["baudrate"], timeout=2) as ser:
                    print(f"{Fore.GREEN}*** Openning UART - COMPORT: {parameters["port"]}, baudrate: {parameters["baudrate"]} ***\n")
                    
                    # Reset the input and output buffers
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()

                    # # Check if the baudrate is different from the flash_baud_rate
                    # if(parameters["baudrate"] != flash_baud_rate):
                    #     # Updating the serial baudrate
                    #     parameters["baudrate"] = flash_baud_rate
                    #     update_flash_baudrate(parameters, ser)
                        


                    flash_nina_fw(parameters, ser)


                    # Wait for the +STARTUP message
                    r = ser.read()				  
                    #Read response until STARTUP received
                    while (str.find(r.decode(),"+STARTUP") < 0):
                        r = r + ser.read()
                    print(f"{Fore.YELLOW}{Style.DIM}+STARTUP received")

                    at_command = "ATI9"
                    ser.write(at_command.encode() + b"\r\n")
                    resp = ser.read(55).decode()
                    resp = resp[resp.find('"'):resp.rfind('"') + 1]
                    print(f"{Fore.GREEN}*** Firmware Version: {resp} ***")	
                    print(f"{Fore.GREEN}*** Closing the serial port! ***\n")
                    ser.close()

            except serial.SerialException as e:
                print(f"{Fore.RED}Error: {e}")

        elif parameters["module"] in nora_family:
            print(f"{Fore.RED}TODO: {parameters["module"]}")
            return None
    else:
        print(f"{Fore.RED}Error: Unsupported module {parameters["module"]}")
        return None

    # except serial.SerialException as e:
    #     print(f"{Fore.RED}Error: {e}")

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