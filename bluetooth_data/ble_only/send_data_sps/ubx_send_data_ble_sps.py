import argparse
import random
import string
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

try:
    from bleak import BleakClient
except ImportError:
    BleakClient = None

def generate_random_data(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def data_to_hex(data):
    return ''.join(f"{ord(char):02X}" for char in data)

async def find_service_and_characteristic(client, service_uuid, characteristic_uuid):
    """
    Finds and returns the specific service and characteristic UUIDs.

    :param client: The BleakClient instance.
    :param service_uuid: The UUID of the service to match.
    :param characteristic_uuid: The UUID of the characteristic to match.
    :return: The matched service and characteristic UUIDs, or None if not found.
    """
    if client.is_connected:
        print(Fore.CYAN + f"Connected to {client.address}")
        
        # Get all services
        services = client.services
        for service in services:
            if service.uuid == service_uuid:
                print(Fore.CYAN + f"Matching service found: {service.uuid}")
                for characteristic in service.characteristics:
                    if characteristic.uuid == characteristic_uuid:
                        print(Fore.CYAN + f"Matching characteristic found: {characteristic.uuid}")
                        return service.uuid, characteristic.uuid

        print(Fore.RED + "No matching service or characteristic found.")
        return None, None

async def send_data_via_ble(client, data, service_uuid, characteristic_uuid):
    """
    Sends data via Bluetooth Low Energy (BLE).

    :param client: The BleakClient instance.
    :param data: The data to send.
    :param service_uuid: The UUID of the service to match.
    :param characteristic_uuid: The UUID of the characteristic to match.
    """
    service_uuid, characteristic_uuid = await find_service_and_characteristic(client, service_uuid, characteristic_uuid)
    
    if service_uuid and characteristic_uuid:
        await client.start_notify(characteristic_uuid, notification_handler)
        await client.write_gatt_char(characteristic_uuid, data.encode())
        hex_data = data_to_hex(data)
        print(Fore.GREEN + f"Sent data: {data}")
        print(Fore.GREEN + f"Sent data in hex: {hex_data}")
        await asyncio.sleep(1)  # Wait for notification
        await client.stop_notify(characteristic_uuid)
    else:
        print(Fore.RED + "Service or characteristic not found. Cannot send data.")

def notification_handler(sender, data):
    """
    Handles notifications from the BLE device.

    :param sender: The sender of the notification.
    :param data: The data received in the notification.
    """
    hex_data = ' '.join(f"{byte:02X}" for byte in data)
    print(Fore.YELLOW + f"Notification from {sender}: {hex_data}")

async def main_ble(target_address):
    """
    Main function to handle BLE connection and data transmission.

    :param target_address: The target Bluetooth address.
    """
    service_uuid = "2456e1b9-26e2-8f83-e744-f34f01e9d701"
    characteristic_uuid = "2456e1b9-26e2-8f83-e744-f34f01e9d703"
    
    try:
        if BleakClient is None:
            raise ImportError("bleak library is not installed")
        
        async with BleakClient(target_address) as client:
            print(Fore.CYAN + f"Connected to {target_address} via BLE")

            while True:
                length = int(input("Enter the number of characters for the data: ").strip())
                data = generate_random_data(length)

                await send_data_via_ble(client, data, service_uuid, characteristic_uuid)
                
                more = input("Do you want to send more data? (Y/N): ").strip().lower()
                if more != 'y' and more != '':
                    break
    except Exception as e:
        print(Fore.RED + f"BLE error: {e}")

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
    args = parser.parse_args()
    
    target_address = format_mac_address(args.address)
    
    asyncio.run(main_ble(target_address))
