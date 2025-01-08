import bluetooth
import argparse
import random
import string
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

try:
    from bleak import BleakClient, BleakError
except ImportError:
    BleakClient = None

def generate_random_data(length):
    """
    Generates a random string of the specified length.

    :param length: The length of the random string.
    :return: A random string of the specified length.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def data_to_hex(data):
    """
    Converts a string to its hexadecimal representation.

    :param data: The string to convert.
    :return: The hexadecimal representation of the string.
    """
    return ''.join(f"{ord(char):02X}" for char in data)

def send_data_via_bluetooth_classic(sock, data):
    """
    Sends data via Bluetooth Classic.

    :param sock: The Bluetooth socket.
    :param data: The data to send.
    """
    try:
        # Send data
        sock.send(data)
        hex_data = data_to_hex(data)
        print(Fore.GREEN + f"Sent data: {hex_data}")
    except bluetooth.BluetoothError as e:
        print(Fore.RED + f"Bluetooth error: {e}")

async def find_service_and_characteristic(client, service_prefix, characteristic_prefix):
    """
    Finds and returns the first service and characteristic UUIDs that match the given prefixes.

    :param client: The BleakClient instance.
    :param service_prefix: The prefix of the service UUID to match.
    :param characteristic_prefix: The prefix of the characteristic UUID to match.
    :return: The matched service and characteristic UUIDs, or None if not found.
    """
    if client.is_connected:
        print(Fore.CYAN + f"Connected to {client.address}")
        
        # Get all services
        services = client.services
        for service in services:
            if service.uuid.startswith(service_prefix):
                print(Fore.CYAN + f"Matching service found: {service.uuid}")
                for characteristic in service.characteristics:
                    if characteristic.uuid.startswith(characteristic_prefix):
                        print(Fore.CYAN + f"Matching characteristic found: {characteristic.uuid}")
                        return service.uuid, characteristic.uuid

        print(Fore.RED + "No matching service or characteristic found.")
        return None, None

async def write_gatt_char_ble(client, data, service_prefix, characteristic_prefix):
    """
    Sends data via Bluetooth Low Energy (BLE).

    :param client: The BleakClient instance.
    :param data: The data to send.
    :param service_prefix: The prefix of the service UUID to match.
    :param characteristic_prefix: The prefix of the characteristic UUID to match.
    """
    service_uuid, characteristic_uuid = await find_service_and_characteristic(client, service_prefix, characteristic_prefix)
    
    if service_uuid and characteristic_uuid:
        # Limit the data length to 244 bytes as per u-blox documentation
        # Document: u-connectXpress_UserGuide_UBX-16024251
        # Section: 12.2 GATT Define a characteristic +UBTGCHA
        if len(data) > 244:
            data = data[:244]
            print(Fore.YELLOW + "Data length exceeds 244 bytes. See ublox documentation.")
        
        await client.write_gatt_char(characteristic_uuid, data.encode())
        hex_data = data_to_hex(data)
        print(Fore.GREEN + f"Sent data: {hex_data}")
    else:
        print(Fore.RED + "Service or characteristic not found. Cannot send data.")

async def read_gatt_char_value(client, service_prefix, characteristic_prefix):
    """
    Finds the matching service and characteristic and reads data from the Bluetooth device.

    :param client: The BleakClient instance.
    :param service_prefix: The prefix of the service UUID to match.
    :param characteristic_prefix: The prefix of the characteristic UUID to match.
    """
    service_uuid, characteristic_uuid = await find_service_and_characteristic(client, service_prefix, characteristic_prefix)

    if service_uuid and characteristic_uuid:
        if client.is_connected:
            print(Fore.CYAN + f"Reading data from characteristic {characteristic_uuid}...")
            data = await client.read_gatt_char(characteristic_uuid)

            # Convert the bytes data to a hex string and print it
            hex_data = ' '.join(f"{byte:02X}" for byte in data)
            print(Fore.GREEN + f"Data read: {hex_data}")
    else:
        print(Fore.RED + "Service or characteristic not found. Cannot read data.")

async def main_ble(target_address, service_prefix="4906276b", characteristic_prefix="49af5250"):
    """
    Sends data via Bluetooth Low Energy (BLE) and reads the characteristic value after writing.

    :param target_address: The target Bluetooth address.
    :param service_prefix: The prefix of the service UUID to match.
    :param characteristic_prefix: The prefix of the characteristic UUID to match.
    """
    try:
        if BleakClient is None:
            raise ImportError("bleak library is not installed")
        
        async with BleakClient(target_address) as client:
            print(Fore.CYAN + f"Connected to {target_address} via BLE")

            while True:
                length = int(input("Enter the number of characters for the data: ").strip())
                data = generate_random_data(length)

                await write_gatt_char_ble(client, data, service_prefix, characteristic_prefix)
                await read_gatt_char_value(client, service_prefix, characteristic_prefix)
                
                more = input("Do you want to send more data? (Y/N): ").strip().lower()
                if more != 'y' and more != '':
                    break
    except Exception as e:
        print(Fore.RED + f"BLE error: {e}")

def main_classic(target_address, port):
    """
    Sends data via Bluetooth Classic.

    :param target_address: The target Bluetooth address.
    :param port: The port to connect to.
    """
    # Create a Bluetooth socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    
    try:
        # Connect to the target Bluetooth device
        sock.connect((target_address, port))
        print(Fore.CYAN + f"Connected to {target_address} on port {port}")
        
        while True:
            length = int(input("Enter the number of characters for the data: ").strip())
            data = generate_random_data(length)
            send_data_via_bluetooth_classic(sock, data)
            
            more = input("Do you want to send more data? (Y/N): ").strip().lower()
            if more != 'y' and more != '':
                break
    except bluetooth.BluetoothError as e:
        print(Fore.RED + f"Bluetooth error: {e}")
    finally:
        # Close the socket
        sock.close()
        print(Fore.CYAN + "Connection closed")

def format_mac_address(mac):
    """
    Formats the MAC address to include colons if they are missing.

    :param mac: The MAC address as a string.
    :return: The formatted MAC address.
    """
    if ':' not in mac:
        mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    return mac

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send data via Bluetooth")
    parser.add_argument("-a", "--address", required=True, help="Target Bluetooth address")
    parser.add_argument("-t", "--type", choices=["classic", "ble"], required=True, help="Type of Bluetooth connection (classic or ble)")
    args = parser.parse_args()
    
    service_prefix = "4906276b"
    characteristic_prefix = "49af5250"

    target_address = format_mac_address(args.address)
    port = 1  # Commonly used port for RFCOMM
    
    if args.type == "classic":
        main_classic(target_address, port)
    elif args.type == "ble":
        asyncio.run(main_ble(target_address, service_prefix, characteristic_prefix))
