import bluetooth
import argparse
import random
import string
import asyncio
import math
from colorama import init, Fore, Style

init(autoreset=True)

try:
    from bleak import BleakClient, BleakError
except ImportError:
    BleakClient = None

debug = False

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
        if debug:
            print(Fore.GREEN + f"Sending {len(data)} bytes:\n{data}")
    except bluetooth.BluetoothError as e:
        print(Fore.RED + f"Bluetooth error: {e}")

async def find_service_and_characteristic(client, service_uuid, characteristic_uuid):
    """
    Finds and returns the service and characteristic UUIDs that match the given UUIDs.

    :param client: The BleakClient instance.
    :param service_uuid: The service UUID to match.
    :param characteristic_uuid: The characteristic UUID to match.
    :return: The matched service and characteristic UUIDs, or None if not found.
    """
    if client.is_connected:
        if debug:
            print(Fore.CYAN + f"Connected to {client.address}")
        
        # Get all services
        services = client.services
        for service in services:
            if service.uuid == service_uuid:
                if debug:
                    print(Fore.CYAN + f"Matching service found: {service.uuid}")
                for characteristic in service.characteristics:
                    if characteristic.uuid == characteristic_uuid:
                        if debug:
                            print(Fore.CYAN + f"Matching characteristic found: {characteristic.uuid}")
                        return service.uuid, characteristic.uuid

        print(Fore.RED + "No matching service or characteristic found.")
        return None, None

async def send_data_sps(client, data, characteristic_uuid):
    """
    Sends data via Bluetooth Low Energy (BLE) using SPS.

    :param client: The BleakClient instance.
    :param data: The data to send.
    :param characteristic_uuid: The characteristic UUID to match.
    """
    
    await client.start_notify(characteristic_uuid, notification_handler)
    await client.write_gatt_char(characteristic_uuid, data.encode())
    
    if debug:
        print(Fore.GREEN + f"Sending {len(data)} bytes:\n{data}")

    await asyncio.sleep(1)  # Wait for notification
    await client.stop_notify(characteristic_uuid)

async def write_data_gatt(client, data, characteristic_uuid):
    """
    Sends data via Bluetooth Low Energy (BLE) for customized services and characteristics.

    :param client: The BleakClient instance.
    :param data: The data to send.
    :param characteristic_uuid: The characteristic UUID to match.
    """
    
    # Limit the data length to 244 bytes as per u-blox documentation
    # Document: u-connectXpress-ATCommands-Manual_UBX-14044127
    # Section: 12.2 GATT Define a characteristic +UBTGCHA
    assert len(data) <= 244, "Data size exceeds the maximum limit of 244 bytes"
    
    await client.write_gatt_char(characteristic_uuid, data.encode())
    hex_data = data_to_hex(data)
    if debug:
        print(Fore.GREEN + f"Sending {len(data)} bytes:\n{hex_data}")

def notification_handler(sender, data):
    """
    Handles notifications from the BLE device.

    :param sender: The sender of the notification.
    :param data: The data received in the notification.
    """
    hex_data = ' '.join(f"{byte:02X}" for byte in data)
    print(Fore.YELLOW + f"Notification from {sender}: {hex_data}")

async def write_gatt_char_ble(client, data, service_uuid, characteristic_uuid):
    """
    Sends data via Bluetooth Low Energy (BLE).

    :param client: The BleakClient instance.
    :param data: The data to send.
    :param service_uuid: The service UUID to match.
    :param characteristic_uuid: The characteristic UUID to match.
    """
    service_uuid, characteristic_uuid = await find_service_and_characteristic(client, service_uuid, characteristic_uuid)
    
    if service_uuid and characteristic_uuid:
        # Check if the service and characteristic UUIDs start with "2456e1b9"
        if service_uuid.startswith("2456e1b9") and characteristic_uuid.startswith("2456e1b9"):
            await send_data_sps(client, data, characteristic_uuid)
        else:
            await write_data_gatt(client, data, characteristic_uuid)
    else:
        print(Fore.RED + "Service or characteristic not found. Cannot send data.")

async def read_gatt_char_value(client, data, service_uuid, characteristic_uuid, sps=False):
    """
    Finds the matching service and characteristic and reads data from the Bluetooth device.

    :param client: The BleakClient instance.
    :param service_uuid: The service UUID to match.
    :param characteristic_uuid: The characteristic UUID to match.
    """
    service_uuid, characteristic_uuid = await find_service_and_characteristic(client, service_uuid, characteristic_uuid)

    if service_uuid and characteristic_uuid:
        if client.is_connected:
            if debug:
                print(Fore.CYAN + f"Reading data from characteristic {characteristic_uuid}...")
            data_receive = await client.read_gatt_char(characteristic_uuid)

            assert data == data_receive.decode(), "Data read does not match data sent"
            print(Fore.YELLOW + "Data read matches data sent")
            if sps:
                # Convert the bytes data to a string and print it
                data_receive = data_receive.decode()
                if debug:
                    print(Fore.GREEN + f"Data read: {data_receive}")
            else:
                # Convert the bytes data to a hex string and print it
                hex_data = ' '.join(f"{byte:02X}" for byte in data_receive)
                if debug:
                    print(Fore.GREEN + f"Data read: {hex_data}")
    else:
        print(Fore.RED + "Service or characteristic not found. Cannot read data.")

async def main_ble(target_address, service_uuid, characteristic_uuid, max_data_size, xtimes):
    """
    Sends data via Bluetooth Low Energy (BLE) and reads the characteristic value after writing.

    :param target_address: The target Bluetooth address.
    :param service_uuid: The service UUID to match.
    :param characteristic_uuid: The characteristic UUID to match.
    :param max_data_size: The maximum number of data to generate.
    :param xtimes: The number of times the script should run.
    """
    try:
        # assert max_data_size <= 4148, "Data size exceeds the maximum limit of 4148 bytes"

        if BleakClient is None:
            raise ImportError("bleak library is not installed")
        
        async with BleakClient(target_address) as client:
            print(Fore.CYAN + f"Connected to {target_address} via BLE")

            if xtimes == 0:
                data = generate_random_data(max_data_size)
                await write_gatt_char_ble(client, data, service_uuid, characteristic_uuid)
                await read_gatt_char_value(client, data, service_uuid, characteristic_uuid, True)
            else:
                for i in range(1, max_data_size + 1):
                    for _ in range(xtimes):
                        data = generate_random_data(i)
                        await write_gatt_char_ble(client, data, service_uuid, characteristic_uuid)
                        await read_gatt_char_value(client, data, service_uuid, characteristic_uuid)
                        await asyncio.sleep(1)
    except Exception as e:
        print(Fore.RED + f"BLE error: {e}")

async def main_classic(target_address, port, max_data_size, xtimes):
    """
    Sends data via Bluetooth Classic.

    :param target_address: The target Bluetooth address.
    :param port: The port to connect to.
    :param max_data_size: The maximum number of data to generate.
    :param xtimes: The number of times the script should run.
    """

    div_data = 2500
    # Create a Bluetooth socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    
    try:
        # Connect to the target Bluetooth device
        sock.connect((target_address, port))
        if debug:
            print(Fore.CYAN + f"Connected to {target_address} on port {port}")
        
        if xtimes == 0:
            data = generate_random_data(max_data_size)
            send_data_via_bluetooth_classic(sock, data)
            await asyncio.sleep(math.ceil(len(data) / div_data) + 1) # Wait for data to be read by u-blox module
        else:
            for i in range(1, max_data_size + 1):
                for _ in range(xtimes):
                    data = generate_random_data(i)
                    send_data_via_bluetooth_classic(sock, data)
                    await asyncio.sleep(math.ceil(len(data) / div_data) + 1) # Wait for data to be read by u-blox module
    except bluetooth.BluetoothError as e:
        print(Fore.RED + f"Bluetooth error: {e}")
    finally:
        # Close the socket
        sock.close()
        if debug:
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
    parser.add_argument("--data_size", type=int, required=True, help="Maximum number of characters to send")
    parser.add_argument("--xtimes", type=int, required=True, help="Number of times the script should run for each data size")
    parser.add_argument("--debug", action="store_true", help="Enable debug messages")
    args = parser.parse_args()
    
    debug = args.debug
    
    service_uuid = "2456e1b9-26e2-8f83-e744-f34f01e9d701"
    characteristic_uuid = "2456e1b9-26e2-8f83-e744-f34f01e9d703"

    target_address = format_mac_address(args.address)
    port = 1  # Commonly used port for RFCOMM
    
    if args.type == "classic":
        asyncio.run(main_classic(target_address, port, args.data_size, args.xtimes))
    elif args.type == "ble":
        asyncio.run(main_ble(target_address, service_uuid, characteristic_uuid, args.data_size, args.xtimes))
