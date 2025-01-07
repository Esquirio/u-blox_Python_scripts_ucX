import asyncio
import sys
import argparse
from bleak import BleakClient, BleakError
from colorama import init, Fore, Style

init(autoreset=True)

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
            # print(f"Service UUID: {service.uuid}, Description: {service.description}") # for debugging
            if service.uuid.startswith(service_prefix):
                print(Fore.CYAN + f"Matching service found: {service.uuid}")
                for characteristic in service.characteristics:
                    # print(f"  Characteristic UUID: {characteristic.uuid}, Properties: {characteristic.properties}") # for debugging
                    if characteristic.uuid.startswith(characteristic_prefix):
                        print(Fore.CYAN + f"Matching characteristic found: {characteristic.uuid}")
                        return service.uuid, characteristic.uuid

        print(Fore.RED + "No matching service or characteristic found.")
        return None, None

async def write_gatt_char_value(client, service_prefix, characteristic_prefix, data_bytes):
    """
    Finds the matching service and characteristic and sends a specific byte value to the Bluetooth device.

    :param client: The BleakClient instance.
    :param service_prefix: The prefix of the service UUID to match.
    :param characteristic_prefix: The prefix of the characteristic UUID to match.
    :param data_bytes: The data to send as bytes.
    """
    service_uuid, characteristic_uuid = await find_service_and_characteristic(client, service_prefix, characteristic_prefix)

    if service_uuid and characteristic_uuid:
        if client.is_connected:
            print(Fore.CYAN + f"Sending {len(data_bytes)} byte(s) to characteristic {characteristic_uuid}...")
            await client.write_gatt_char(characteristic_uuid, data_bytes)
            hex_data = ' '.join(f"{byte:02X}" for byte in data_bytes)
            print(Fore.GREEN + f"Data {hex_data} sent successfully!")
    else:
        print(Fore.RED + "Service or characteristic not found. Cannot send data.")

def format_mac_address(mac):
    """
    Formats the MAC address to include colons if they are missing.

    :param mac: The MAC address as a string.
    :return: The formatted MAC address.
    """
    if ':' not in mac:
        mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    return mac

def data_to_hex(data):
    return ''.join(f"{byte:02X}" for byte in data)

async def main(target_address):
    service_prefix = "4906276b"
    characteristic_prefix = "49af5250"
    value1 = b'\x00'  # Byte value to send (0x00 in hexadecimal)
    value2 = b'\x23'  # Byte value to send (0x23 in hexadecimal)

    try:
        async with BleakClient(target_address) as client:
            if client.is_connected:
                await write_gatt_char_value(client, service_prefix, characteristic_prefix, value1)
                await read_gatt_char_value(client, service_prefix, characteristic_prefix)
                await write_gatt_char_value(client, service_prefix, characteristic_prefix, value2)
                await read_gatt_char_value(client, service_prefix, characteristic_prefix)
    except BleakError as e:
        print(Fore.RED + f"Failed to connect to {target_address}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bluetooth GATT read/write script")
    parser.add_argument('-a', '--address', required=True, help="MAC address of the Bluetooth device")
    args = parser.parse_args()

    target_address = format_mac_address(args.address)
    asyncio.run(main(target_address))
