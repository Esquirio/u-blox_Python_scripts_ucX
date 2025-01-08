import asyncio
import sys
import argparse
import re
from bleak import BleakClient, BleakScanner
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def format_mac_address(address):
    if re.match(r"^[0-9A-Fa-f]{12}$", address):
        return ":".join(address[i:i+2] for i in range(0, 12, 2))
    elif re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", address):
        return address
    else:
        raise ValueError("Invalid MAC address format")

async def find_service_and_characteristic(device_address):
    try:
        async with BleakClient(device_address) as client:
            services = await client.get_services()
            
            if not services:
                print(Fore.RED + "No services found.")
                return None, None
            
            for service in services:
                print(Fore.GREEN + f"Service UUID: {service.uuid}")
                for char in service.characteristics:
                    print(Fore.CYAN + f"    Characteristic UUID: {char.uuid}")
                    print(Fore.YELLOW + f"        Properties: {char.properties}")
                    try:
                        if "read" in char.properties:
                            value = await client.read_gatt_char(char.uuid)
                            print(Fore.MAGENTA + f"        Value: {value}")
                        else:
                            print(Fore.MAGENTA + f"        Value: Not readable")
                    except Exception as e:
                        print(Fore.RED + f"        Value: Could not read ({e})")
            
            # Return the first service and characteristic found (if needed)
            first_service = next(iter(services))
            first_characteristic = next(iter(first_service.characteristics)) if first_service.characteristics else None
            
            return first_service, first_characteristic
    
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        return None, None

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find BLE services and characteristics.")
    parser.add_argument("-a", "--address", required=True, help="MAC address of the BLE device")
    args = parser.parse_args()
    
    try:
        device_address = format_mac_address(args.address)
    except ValueError as e:
        print(Fore.RED + str(e))
        sys.exit(1)

    # Run the async function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(find_service_and_characteristic(device_address))